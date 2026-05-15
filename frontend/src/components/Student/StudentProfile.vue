<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <div>
        <button class="btn btn-outline-secondary btn-sm" @click="$router.go(-1)" style="margin-right:10px;">← Back</button>
        <span style="font-weight:600;font-size:0.95rem;">My Profile</span>
      </div>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <div v-else style="display:grid;grid-template-columns:2fr 1fr;gap:18px;">
      <!-- Left: Edit form -->
      <div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;">
        <h5 style="margin-bottom:16px;color:#444;">Personal Information</h5>
        <form @submit.prevent="save">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <label class="form-label">Full Name</label>
              <input class="form-control" v-model="form.name" required />
            </div>
            <div>
              <label class="form-label">Roll Number</label>
              <input class="form-control" v-model="form.roll_number" />
            </div>
            <div>
              <label class="form-label">Branch</label>
              <select class="form-select" v-model="form.branch">
                <option value="">Select</option>
                <option>CSE</option><option>ECE</option><option>ME</option>
                <option>EE</option><option>CE</option><option>IT</option><option>Other</option>
              </select>
            </div>
            <div>
              <label class="form-label">CGPA</label>
              <input type="number" class="form-control" v-model="form.cgpa" min="0" max="10" step="0.01" />
            </div>
            <div>
              <label class="form-label">Year</label>
              <select class="form-select" v-model="form.year">
                <option value="">Select</option>
                <option :value="1">1st</option><option :value="2">2nd</option>
                <option :value="3">3rd</option><option :value="4">4th</option>
              </select>
            </div>
            <div>
              <label class="form-label">Phone</label>
              <input class="form-control" v-model="form.phone" placeholder="+91 XXXXX XXXXX" />
            </div>
            <div style="grid-column:1/-1;">
              <label class="form-label">Skills (comma separated)</label>
              <input class="form-control" v-model="form.skills" placeholder="Python, React, SQL..." />
            </div>
          </div>
          <button class="btn btn-primary" style="margin-top:16px;" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- Right: Profile summary + Resume -->
      <div>
        <!-- Profile card -->
        <div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;text-align:center;margin-bottom:14px;">
          <div style="font-size:3rem;">🎓</div>
          <div style="font-weight:700;font-size:1.1rem;margin-top:8px;">{{ form.name }}</div>
          <div style="color:#666;font-size:0.85rem;">{{ student?.email }}</div>
          <div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin-top:10px;">
            <span class="badge badge-applied">{{ form.branch || '?' }}</span>
            <span class="badge badge-closed">Year {{ form.year || '?' }}</span>
            <span class="badge" :class="form.cgpa >= 8 ? 'badge-approved' : form.cgpa >= 6 ? 'badge-pending' : 'badge-rejected'">
              CGPA {{ form.cgpa }}
            </span>
          </div>
          <div v-if="form.skills" style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin-top:10px;">
            <span class="badge" style="background:#e8f0fe;color:#1a73e8;"
              v-for="s in form.skills.split(',').slice(0,5)" :key="s">{{ s.trim() }}</span>
          </div>
        </div>

        <!-- Resume card -->
        <div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;">
          <h6 style="margin-bottom:12px;color:#444;">Resume</h6>
          <a v-if="student?.resume_path"
            :href="`/uploads/${student.resume_path}`" target="_blank"
            class="btn btn-outline-info btn-sm" style="width:100%;display:block;margin-bottom:12px;">
            📄 View Current Resume
          </a>
          <div v-else style="color:#999;font-size:0.85rem;text-align:center;margin-bottom:12px;">
            No resume uploaded yet
          </div>
          <label class="form-label">Upload New (PDF/DOC)</label>
          <input type="file" class="form-control" accept=".pdf,.doc,.docx" @change="onFileChange" ref="resumeInput" />
          <button class="btn btn-outline-primary btn-sm" style="width:100%;margin-top:8px;"
            @click="uploadResume" :disabled="!selectedFile || uploading">
            {{ uploading ? 'Uploading...' : '⬆ Upload' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const student = ref(null)
const form = reactive({})
const loading = ref(true)
const saving = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)
const resumeInput = ref(null)

// Load student profile on mount
onMounted(async () => {
  try {
    const r = await api.get('/student/profile')
    student.value = r.data
    Object.assign(form, {
      name: r.data.name,
      roll_number: r.data.roll_number,
      branch: r.data.branch,
      cgpa: r.data.cgpa,
      year: r.data.year,
      phone: r.data.phone,
      skills: r.data.skills
    })
  } catch (e) {
    showToast('Failed to load profile', 'danger')
  } finally {
    loading.value = false
  }
})

// Save profile changes
async function save() {
  saving.value = true
  try {
    await api.put('/student/profile', form)
    showToast('Profile updated!', 'success')
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed', 'danger')
  } finally {
    saving.value = false
  }
}

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
}

// Upload resume file
async function uploadResume() {
  if (!selectedFile.value) return
  uploading.value = true
  const fd = new FormData()
  fd.append('resume', selectedFile.value)
  try {
    await api.post('/student/profile/resume', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    showToast('Resume uploaded!', 'success')
    const r = await api.get('/student/profile')
    student.value = r.data
    selectedFile.value = null
    if (resumeInput.value) resumeInput.value.value = ''
  } catch (e) {
    showToast(e.response?.data?.error || 'Upload failed', 'danger')
  } finally {
    uploading.value = false
  }
}
</script>
