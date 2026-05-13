import axios from 'axios'
import { reactive } from 'vue'

const api = axios.create({
    baseURL: '/api'
})

// JWT request interceptor
api.interceptors.request.use(config => {
    const token = localStorage.getItem('ppa_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

// 401 response interceptor
api.interceptors.response.use(
    res => res,
    err => {
        if (err.response?.status === 401) {
            authState.logout()
            window.location.href = '/'
        }
        return Promise.reject(err)
    }
)

// Reactive auth state
export const authState = reactive({
    token: localStorage.getItem('ppa_token') || null,
    user: JSON.parse(localStorage.getItem('ppa_user') || 'null'),
    get isLoggedIn() { return !!this.token },
    get role() { return this.user?.role || null },
    get isAdmin() { return this.role === 'admin' },
    get isCompany() { return this.role === 'company' },
    get isStudent() { return this.role === 'student' },
    login(token, user) {
        this.token = token
        this.user = user
        localStorage.setItem('ppa_token', token)
        localStorage.setItem('ppa_user', JSON.stringify(user))
    },
    logout() {
        this.token = null
        this.user = null
        localStorage.removeItem('ppa_token')
        localStorage.removeItem('ppa_user')
    }
})

// Toast state
export const toastState = reactive({ messages: [] })

export function showToast(message, type = 'success') {
    const id = Date.now()
    toastState.messages.push({ id, message, type })
    setTimeout(() => {
        toastState.messages = toastState.messages.filter(m => m.id !== id)
    }, 3500)
}

export default api
