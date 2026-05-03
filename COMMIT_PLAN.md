# 2-Week GitHub Commits Plan for Placement Portal Application

This plan is based on your existing codebase (Flask backend with Vue.js frontend for a placement portal). It focuses on incremental improvements, feature additions, bug fixes, and best practices to create meaningful commits. Each day includes at least 5 commits, spread across development tasks. Aim for commits between 9 AM - 9 PM local time for consistent activity. Use descriptive commit messages (e.g., "feat: add user authentication endpoint").

## Week 1: Backend Enhancements and Core Features
### Day 1: Backend Setup and Models Refinement
1. Refactor models.py: Add validation constraints to User and Company models.
2. Update config.py: Add environment-specific database configurations.
3. Add logging to extensions.py for better error tracking.
4. Create initial migration scripts in a new migrations/ folder.
5. Update requirements.txt: Pin versions for security.

### Day 2: Authentication Improvements
1. Enhance auth.py: Add password reset functionality.
2. Implement JWT token refresh in auth routes.
3. Add rate limiting to login endpoints.
4. Update models.py: Add email verification fields.
5. Add unit tests for auth endpoints in a new tests/ folder.

### Day 3: Admin Routes Expansion
1. Add bulk user import feature in admin.py.
2. Implement admin dashboard statistics endpoint.
3. Add role-based access control checks.
4. Update models.py: Add admin-specific fields.
5. Add input validation middleware.

### Day 4: Company Routes Enhancements
1. Add drive scheduling validation in company.py.
2. Implement company profile update endpoint.
3. Add notification system for drive updates.
4. Update models.py: Add company verification status.
5. Add API documentation comments.

### Day 5: Student Routes Improvements
1. Add application tracking in student.py.
2. Implement resume upload validation.
3. Add student profile completion checks.
4. Update models.py: Add student skills array.
5. Add pagination to student endpoints.

### Day 6: Task Automation and Jobs
1. Enhance jobs.py: Add email notification tasks.
2. Implement background job scheduling.
3. Add error handling for failed tasks.
4. Update requirements.txt: Add Celery for async tasks.
5. Add job monitoring endpoint.

### Day 7: Backend Testing and Cleanup
1. Add integration tests for all routes.
2. Fix any linting issues in backend code.
3. Optimize database queries in models.
4. Add API versioning to routes.
5. Update README.md with backend setup instructions.

## Week 2: Frontend Development and Integration
### Day 8: Frontend Setup and Auth Views
1. Update vite.config.js: Add proxy for backend API.
2. Enhance AuthView.vue: Add form validation.
3. Implement login/logout state management.
4. Add error handling in axios.js.
5. Update package.json: Add form validation library.

### Day 9: Admin Components
1. Improve AdminDashboard.vue: Add charts for stats.
2. Add data tables to AdminStudents.vue.
3. Implement CRUD operations in AdminCompanies.vue.
4. Add responsive design to admin components.
5. Update main.css: Add admin-specific styles.

### Day 10: Company Components
1. Enhance CompanyDashboard.vue: Add drive analytics.
2. Add form validation to CreateDrive.vue.
3. Implement application review in CompanyApplications.vue.
4. Add file upload for company logos.
5. Update router/index.js: Add company route guards.

### Day 11: Student Components
1. Improve StudentProfile.vue: Add profile editing.
2. Add application status tracking in StudentApplications.vue.
3. Implement drive filtering in StudentDrives.vue.
4. Add notifications component.
5. Update main.css: Add student-specific themes.

### Day 12: Integration and API Calls
1. Connect frontend to backend APIs in all components.
2. Add loading states and error handling.
3. Implement real-time updates using WebSockets.
4. Add unit tests for Vue components.
5. Update package.json: Add testing framework.

### Day 13: UI/UX Improvements
1. Add responsive design across all components.
2. Implement dark mode toggle.
3. Add accessibility features (ARIA labels).
4. Optimize bundle size in vite.config.js.
5. Add user feedback forms.

### Day 14: Final Polish and Deployment Prep
1. Add end-to-end tests.
2. Fix any cross-browser issues.
3. Update README.md with full setup and deployment guide.
4. Add environment configuration files.
5. Create Docker setup for easy deployment.

## Tips for Success:
- Commit frequently: Even small changes (e.g., typo fixes) count if meaningful.
- Use branches: Create feature branches for each day's work, merge with pull requests.
- Avoid force pushes: Keep history clean.
- Track progress: Use GitHub's contribution graph to monitor streaks.
- If blocked, focus on documentation or refactoring commits.