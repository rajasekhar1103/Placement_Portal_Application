<template>
  <div>
    <div style="margin-bottom:16px;">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.go(-1)" style="margin-right:10px;">← Back</button>
      <strong>Create Placement Drive</strong>
      <span style="color:#666;font-size:0.85rem;margin-left:8px;">Fill in details to post a new drive</span>
    </div>

    <form @submit.prevent="submit" style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
        <div>
          <label class="form-label">Job Title *</label>
          <input class="form-control" v-model="form.job_title" required placeholder="e.g. Software Engineer" />
        </div>
        <div>
          <label class="form-label">Location</label>
          <input class="form-control" v-model="form.location" placeholder="e.g. Bengaluru" />
        </div>
        <div style="grid-column:1/-1;">
          <label class="form-label">Job Description</label>
          <textarea class="form-control" v-model="form.job_description" rows="4" placeholder="Describe the role..."></textarea>
        </div>
        <div>
          <label class="form-label">Salary / CTC</label>
          <input class="form-control" v-model="form.salary" placeholder="e.g. ₹12 LPA" />
        </div>
        <div>
          <label class="form-label">Interview Type</label>
          <select class="form-select" v-model="form.interview_type">
            <option>In-person</option><option>Virtual</option><option>Hybrid</option>
          </select>
        </div>
        <div>
          <label class="form-label">Application Deadline</label>
          <input type="datetime-local" class="form-control" v-model="form.application_deadline" />
        </div>
      </div>

      <!-- Eligibility section -->
      <hr style="margin:18px 0;" />
      <h6 style="color:#555;margin-bottom:12px;">Eligibility Criteria</h6>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;">
        <div>
          <label class="form-label">Min. CGPA</label>
          <input type="number" class="form-control" v-model="form.eligibility_cgpa" min="0" max="10" step="0.1" placeholder="0.0" />
        </div>
        <div>
          <label class="form-label">Year of Study</label>
          <select class="form-select" v-model="form.eligibility_year">
            <option value="">Any Year</option>
            <option :value="1">1st</option><option :value="2">2nd</option>
            <option :value="3">3rd</option><option :value="4">4th</option>
          </select>
        </div>
        <div>
          <label class="form-label">Eligible Branches</label>
          <input class="form-control" v-model="form.eligibility_branch" placeholder="All or CSE,ECE,IT" />
        </div>
      </div>

      <!-- Error + Submit -->
      <div v-if="error" style="background:#fce8e6;border:1px solid #ea4335;border-radius:6px;padding:8px 12px;color:#c62828;font-size:0.85rem;margin:14px 0;">
        {{ error }}
      </div>
      <button class="btn btn-primary" style="margin-top:16px;" :disabled="loading">
        {{ loading ? 'Submitting...' : '📤 Submit for Approval' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api, { showToast } from '@/api/axios'

const router = useRouter()
const loading = ref(false)
const error = ref('')

// Form data for the new drive
const form = reactive({
  job_title: '',
  job_description: '',
  location: '',
  salary: '',
  interview_type: 'In-person',
  application_deadline: '',
  eligibility_cgpa: '',
  eligibility_year: '',
  eligibility_branch: 'All'
})

// Submit drive to backend
async function submit() {
  loading.value = true
  error.value = ''
  try {
    await api.post('/company/drives', form)
    showToast('Drive submitted for approval!', 'success')
    router.push('/company/drives')
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to create drive'
  } finally {
    loading.value = false
  }
}
</script>
