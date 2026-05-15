<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Title -->
      <div style="text-align:center;margin-bottom:24px;">
        <div class="auth-logo">🎓 PlacementPortal</div>
        <p style="color:#666;margin-top:6px;font-size:0.9rem;">Campus Recruitment Management</p>
      </div>

      <!-- Tab: Student / Company (only on register page) -->
      <div v-if="mode !== 'login'" style="display:flex;margin-bottom:18px;border:1px solid #ddd;border-radius:8px;overflow:hidden;">
        <button
          style="flex:1;padding:9px;border:none;cursor:pointer;font-weight:600;font-size:0.9rem;"
          :style="tab === 'student' ? 'background:#1a73e8;color:white;' : 'background:#f4f6f8;color:#444;'"
          @click="tab = 'student'"
        >Student</button>
        <button
          style="flex:1;padding:9px;border:none;cursor:pointer;font-weight:600;font-size:0.9rem;"
          :style="tab === 'company' ? 'background:#1a73e8;color:white;' : 'background:#f4f6f8;color:#444;'"
          @click="tab = 'company'"
        >Company</button>
      </div>

      <!-- Login Form -->
      <form v-if="mode === 'login'" @submit.prevent="login">
        <div style="margin-bottom:14px;">
          <label class="form-label">Email Address</label>
          <input class="form-control" type="email" v-model="form.email" required placeholder="you@example.com" />
        </div>
        <div style="margin-bottom:14px;">
          <label class="form-label">Password</label>
          <input class="form-control" type="password" v-model="form.password" required placeholder="••••••••" />
        </div>
        <div v-if="error" style="background:#fce8e6;border:1px solid #ea4335;border-radius:6px;padding:8px 12px;color:#c62828;font-size:0.85rem;margin-bottom:12px;">
          {{ error }}
        </div>
        <button class="btn btn-primary" style="width:100%;padding:10px;" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>Sign In</span>
        </button>
        <div style="text-align:center;margin-top:14px;font-size:0.85rem;color:#666;">
          Don't have an account?
          <a href="#" style="color:#1a73e8;" @click.prevent="mode = 'register'">Register here</a>
        </div>
      </form>

      <!-- Student Registration Form -->
      <form v-else-if="mode === 'register' && tab === 'student'" @submit.prevent="registerStudent">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="grid-column:1/-1;">
            <label class="form-label">Full Name</label>
            <input class="form-control" v-model="reg.name" required placeholder="Alice Smith" />
          </div>
          <div style="grid-column:1/-1;">
            <label class="form-label">Email</label>
            <input class="form-control" type="email" v-model="reg.email" required placeholder="alice@student.edu" />
          </div>
          <div>
            <label class="form-label">Password</label>
            <input class="form-control" type="password" v-model="reg.password" required minlength="6" />
          </div>
          <div>
            <label class="form-label">Roll Number</label>
            <input class="form-control" v-model="reg.roll_number" placeholder="CS2024001" />
          </div>
          <div>
            <label class="form-label">Branch</label>
            <select class="form-select" v-model="reg.branch">
              <option value="">Select</option>
              <option>CSE</option><option>ECE</option><option>ME</option>
              <option>EE</option><option>CE</option><option>IT</option>
            </select>
          </div>
          <div>
            <label class="form-label">CGPA</label>
            <input class="form-control" type="number" v-model="reg.cgpa" min="0" max="10" step="0.1" placeholder="8.5" />
          </div>
          <div style="grid-column:1/-1;">
            <label class="form-label">Year</label>
            <select class="form-select" v-model="reg.year">
              <option value="">-</option>
              <option :value="1">1</option><option :value="2">2</option>
              <option :value="3">3</option><option :value="4">4</option>
            </select>
          </div>
        </div>
        <div v-if="error" style="background:#fce8e6;border:1px solid #ea4335;border-radius:6px;padding:8px 12px;color:#c62828;font-size:0.85rem;margin:12px 0;">
          {{ error }}
        </div>
        <button class="btn btn-primary" style="width:100%;padding:10px;margin-top:10px;" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>Register as Student</span>
        </button>
        <div style="text-align:center;margin-top:12px;font-size:0.85rem;">
          <a href="#" style="color:#1a73e8;" @click.prevent="mode = 'login'">← Back to Login</a>
        </div>
      </form>

      <!-- Company Registration Form -->
      <form v-else-if="mode === 'register' && tab === 'company'" @submit.prevent="registerCompany">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div style="grid-column:1/-1;">
            <label class="form-label">Company Name</label>
            <input class="form-control" v-model="reg.company_name" required placeholder="Acme Corp" />
          </div>
          <div style="grid-column:1/-1;">
            <label class="form-label">Email</label>
            <input class="form-control" type="email" v-model="reg.email" required />
          </div>
          <div>
            <label class="form-label">Password</label>
            <input class="form-control" type="password" v-model="reg.password" required minlength="6" />
          </div>
          <div>
            <label class="form-label">Industry</label>
            <input class="form-control" v-model="reg.industry" placeholder="Technology" />
          </div>
          <div>
            <label class="form-label">HR Contact</label>
            <input class="form-control" v-model="reg.hr_contact" placeholder="John HR" />
          </div>
          <div>
            <label class="form-label">Website</label>
            <input class="form-control" v-model="reg.website" placeholder="https://..." />
          </div>
        </div>
        <div v-if="error" style="background:#fce8e6;border:1px solid #ea4335;border-radius:6px;padding:8px 12px;color:#c62828;font-size:0.85rem;margin:12px 0;">
          {{ error }}
        </div>
        <button class="btn btn-primary" style="width:100%;padding:10px;margin-top:10px;" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>Register Company</span>
        </button>
        <div style="text-align:center;margin-top:12px;font-size:0.85rem;">
          <a href="#" style="color:#1a73e8;" @click.prevent="mode = 'login'">← Back to Login</a>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api, { authState, showToast } from '@/api/axios'

const router = useRouter()
const mode = ref('login')           // 'login' or 'register'
const tab = ref('student')          // 'student' or 'company'
const loading = ref(false)
const error = ref('')
const form = reactive({ email: '', password: '' })
const reg = reactive({})            // registration fields

async function login() {
  loading.value = true
  error.value = ''
  try {
    const r = await api.post('/auth/login', form)
    authState.login(r.data.access_token, r.data.user)
    showToast(`Welcome, ${r.data.user.email}!`)
    const map = { admin: '/admin', company: '/company', student: '/student' }
    router.push(map[r.data.user.role] || '/')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}

async function registerStudent() {
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/register/student', reg)
    showToast('Registered! Please log in.', 'success')
    mode.value = 'login'
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}

async function registerCompany() {
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/register/company', reg)
    showToast('Registered! Awaiting admin approval.', 'success')
    mode.value = 'login'
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
