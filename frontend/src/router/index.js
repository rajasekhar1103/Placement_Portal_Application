import { createRouter, createWebHashHistory } from 'vue-router'
import { authState } from '@/api/axios'

import AuthView from '@/components/Auth/AuthView.vue'
import AdminDashboard from '@/components/Admin/AdminDashboard.vue'
import AdminCompanies from '@/components/Admin/AdminCompanies.vue'
import AdminStudents from '@/components/Admin/AdminStudents.vue'
import AdminDrives from '@/components/Admin/AdminDrives.vue'
import AdminApplications from '@/components/Admin/AdminApplications.vue'
import CompanyDashboard from '@/components/Company/CompanyDashboard.vue'
import CompanyDrives from '@/components/Company/CompanyDrives.vue'
import CreateDrive from '@/components/Company/CreateDrive.vue'
import CompanyApplications from '@/components/Company/CompanyApplications.vue'
import StudentDashboard from '@/components/Student/StudentDashboard.vue'
import StudentDrives from '@/components/Student/StudentDrives.vue'
import StudentApplications from '@/components/Student/StudentApplications.vue'
import StudentProfile from '@/components/Student/StudentProfile.vue'

const routes = [
    { path: '/', component: AuthView },

    {
        path: '/admin',
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            { path: '', component: AdminDashboard },
            { path: 'companies', component: AdminCompanies },
            { path: 'students', component: AdminStudents },
            { path: 'drives', component: AdminDrives },
            { path: 'applications', component: AdminApplications }
        ]
    },

    {
        path: '/company',
        meta: { requiresAuth: true, role: 'company' },
        children: [
            { path: '', component: CompanyDashboard },
            { path: 'drives', component: CompanyDrives },
            { path: 'drives/create', component: CreateDrive },
            { path: 'drives/:driveId/applications', component: CompanyApplications, props: true }
        ]
    },

    {
        path: '/student',
        meta: { requiresAuth: true, role: 'student' },
        children: [
            { path: '', component: StudentDashboard },
            { path: 'drives', component: StudentDrives },
            { path: 'applications', component: StudentApplications },
            { path: 'profile', component: StudentProfile }
        ]
    },

    { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(r => r.meta?.requiresAuth)
    if (requiresAuth && !authState.isLoggedIn) { next('/'); return }
    if (requiresAuth && to.meta?.role && authState.role !== to.meta.role) {
        const map = { admin: '/admin', company: '/company', student: '/student' }
        next(map[authState.role] || '/'); return
    }
    if (to.path === '/' && authState.isLoggedIn) {
        const map = { admin: '/admin', company: '/company', student: '/student' }
        next(map[authState.role] || '/'); return
    }
    next()
})

export default router
