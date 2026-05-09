import csv
import io
import os
import logging
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Celery is initialized in app.py via make_celery()
# This file just defines the tasks; they run within app context via ContextTask


def get_celery():
    from app import celery
    return celery


celery_app = get_celery()


@celery_app.task(bind=True, name="tasks.send_daily_reminders")
def send_daily_reminders(self):
    """
    Runs daily. Sends email reminders to students whose applied drives
    have deadlines within the next 3 days.
    """
    try:
        from extensions import db, mail
        from models.models import Application, PlacementDrive, Student
        from flask_mail import Message

        now = datetime.utcnow()
        soon = now + timedelta(days=3)

        # Find drives with deadlines within 3 days
        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == "approved",
            PlacementDrive.application_deadline >= now,
            PlacementDrive.application_deadline <= soon,
        ).all()

        reminders_sent = 0
        for drive in upcoming_drives:
            applications = drive.applications.filter_by(status="applied").all()
            for app in applications:
                student = app.student
                if not student or not student.user or not student.user.is_active:
                    continue
                try:
                    msg = Message(
                        subject=f"⏰ Reminder: {drive.job_title} at {drive.company.company_name} closes soon!",
                        recipients=[student.user.email],
                        html=f"""
                        <h2>Placement Drive Deadline Reminder</h2>
                        <p>Dear {student.name},</p>
                        <p>The application deadline for <strong>{drive.job_title}</strong> at 
                        <strong>{drive.company.company_name}</strong> is approaching.</p>
                        <p><strong>Deadline:</strong> {drive.application_deadline.strftime('%B %d, %Y at %H:%M UTC')}</p>
                        <p>Please ensure your profile is complete and your resume is updated.</p>
                        <br><p>Best regards,<br>Placement Portal Team</p>
                        """,
                    )
                    mail.send(msg)
                    reminders_sent += 1
                except Exception as e:
                    logger.error(f"Failed to send reminder to {student.user.email}: {e}")

        logger.info(f"Daily reminders: {reminders_sent} sent for {len(upcoming_drives)} drives")
        return {"status": "done", "reminders_sent": reminders_sent}
    except Exception as exc:
        logger.error(f"send_daily_reminders failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="tasks.send_monthly_report")
def send_monthly_report(self):
    """
    Runs on the 1st of every month. Sends HTML activity report to admin.
    """
    try:
        from extensions import db, mail
        from models.models import User, Company, Student, PlacementDrive, Application
        from flask_mail import Message
        from config import Config

        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 1:
            prev_month_start = month_start.replace(year=now.year - 1, month=12)
        else:
            prev_month_start = month_start.replace(month=now.month - 1)

        drives_this_month = PlacementDrive.query.filter(
            PlacementDrive.created_at >= prev_month_start,
            PlacementDrive.created_at < month_start,
        ).count()

        apps_this_month = Application.query.filter(
            Application.application_date >= prev_month_start,
            Application.application_date < month_start,
        ).count()

        selected_this_month = Application.query.filter(
            Application.application_date >= prev_month_start,
            Application.application_date < month_start,
            Application.status == "selected",
        ).count()

        new_companies = Company.query.filter(
            Company.created_at >= prev_month_start,
            Company.created_at < month_start,
        ).count()

        new_students = Student.query.filter(
            Student.created_at >= prev_month_start,
            Student.created_at < month_start,
        ).count()

        month_name = prev_month_start.strftime("%B %Y")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 20px; }}
                h1 {{ color: #1a237e; }}
                .stat-card {{ background: #e8eaf6; border-radius: 8px; padding: 15px; margin: 10px 0; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #3949ab; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background: #3949ab; color: white; padding: 10px; }}
                td {{ padding: 8px; border: 1px solid #ccc; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>📊 Monthly Placement Report – {month_name}</h1>
            <p>Generated on: {now.strftime("%B %d, %Y")}</p>
            <hr>
            <table>
                <tr><th>Metric</th><th>Count</th></tr>
                <tr><td>New Companies Registered</td><td class='stat-value'>{new_companies}</td></tr>
                <tr><td>New Students Registered</td><td class='stat-value'>{new_students}</td></tr>
                <tr><td>Placement Drives Created</td><td class='stat-value'>{drives_this_month}</td></tr>
                <tr><td>Total Applications Received</td><td class='stat-value'>{apps_this_month}</td></tr>
                <tr><td>Students Selected</td><td class='stat-value'>{selected_this_month}</td></tr>
                <tr><td>Selection Rate</td><td class='stat-value'>{
                    f"{(selected_this_month/apps_this_month*100):.1f}%" if apps_this_month > 0 else "N/A"
                }</td></tr>
            </table>
            <p>This is an automated report generated by the Placement Portal Application.</p>
        </body>
        </html>
        """

        admin_user = User.query.filter_by(role="admin").first()
        if admin_user:
            msg = Message(
                subject=f"📊 Monthly Placement Report – {month_name}",
                recipients=[admin_user.email],
                html=html,
            )
            mail.send(msg)
            logger.info(f"Monthly report sent to {admin_user.email}")

        return {"status": "done", "month": month_name}
    except Exception as exc:
        logger.error(f"send_monthly_report failed: {exc}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)


@celery_app.task(bind=True, name="tasks.export_applications_csv")
def export_applications_csv(self, student_id):
    """
    Async job: generates CSV of all student applications and emails it to them.
    """
    try:
        from extensions import db, mail
        from models.models import Student, Application
        from flask_mail import Message

        student = Student.query.get(student_id)
        if not student:
            return {"status": "error", "reason": "Student not found"}

        apps = student.applications.order_by(Application.application_date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Application ID", "Student ID", "Student Name", "Company Name",
                         "Drive Title", "Application Date", "Status", "Remarks", "Interview Date"])
        for a in apps:
            writer.writerow([
                a.id, student.id, student.name,
                a.drive.company.company_name if a.drive and a.drive.company else "",
                a.drive.job_title if a.drive else "",
                a.application_date.strftime("%Y-%m-%d") if a.application_date else "",
                a.status,
                a.remarks or "",
                a.interview_date.strftime("%Y-%m-%d") if a.interview_date else "",
            ])

        csv_content = output.getvalue()
        filename = f"applications_{student.id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"

        # Save to disk
        export_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        with open(filepath, "w", newline="") as f:
            f.write(csv_content)

        # Email the CSV
        msg = Message(
            subject="✅ Your Application History Export is Ready",
            recipients=[student.user.email],
            html=f"""
            <h2>Application History Export</h2>
            <p>Dear {student.name},</p>
            <p>Your placement application history export with <strong>{len(apps)} records</strong> is attached.</p>
            <br><p>Best regards,<br>Placement Portal Team</p>
            """,
        )
        with open(filepath, "rb") as f:
            msg.attach(filename, "text/csv", f.read())
        mail.send(msg)

        logger.info(f"CSV export sent to {student.user.email}")
        return {"status": "done", "records": len(apps), "file": filename}
    except Exception as exc:
        logger.error(f"export_applications_csv failed: {exc}")
        raise self.retry(exc=exc, countdown=30, max_retries=3)


# ── Beat Schedule ────────────────────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    "daily-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM daily
    },
    "monthly-report": {
        "task": "tasks.send_monthly_report",
        "schedule": crontab(hour=6, minute=0, day_of_month=1),  # 1st of month at 6AM
    },
}
