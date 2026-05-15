<template>
  <div>
    <div style="margin-bottom:16px;">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.go(-1)" style="margin-right:10px;">← Back</button>
      <strong>Applications</strong>
      <span style="color:#666;font-size:0.85rem;margin-left:8px;" v-if="driveInfo">— {{ driveInfo.job_title }}</span>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>
    <div v-else>
      <!-- Filters -->
      <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;">
        <input class="form-control" style="max-width:220px;" v-model="search" placeholder="Search students..." />
        <select class="form-select" style="max-width:180px;" v-model="statusFilter">
          <option value="">All Status</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
          <option value="waitlisted">Waitlisted</option>
        </select>
      </div>

      <!-- Table -->
      <div style="overflow-x:auto;">
        <table class="simple-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>CGPA</th>
              <th>Branch</th>
              <th>Applied</th>
              <th>Status</th>
              <th>Resume</th>
              <th>Update Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>
                <div style="font-weight:600;">{{ a.student_name }}</div>
                <div style="color:#666;font-size:0.82rem;">{{ a.student_email }}</div>
              </td>
              <td>
                <span class="badge" :class="cgpaBadge(a.student_cgpa)">{{ a.student_cgpa }}</span>
              </td>
              <td>{{ a.student_branch }}</td>
              <td>{{ a.application_date ? new Date(a.application_date).toLocaleDateString('en-IN') : '—' }}</td>
              <td>
                <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
              </td>
              <td>
                <a v-if="a.resume_path" :href="`/uploads/${a.resume_path}`" target="_blank"
                  class="btn btn-outline-info btn-sm">📄</a>
                <span v-else style="color:#999;">—</span>
              </td>
              <td>
                <!-- Select new status and save -->
                <div style="display:flex;gap:5px;">
                  <select class="form-select" style="max-width:140px;padding:4px 8px;font-size:0.82rem;" v-model="a._newStatus">
                    <option value="applied">Applied</option>
                    <option value="shortlisted">Shortlisted</option>
                    <option value="selected">Selected</option>
                    <option value="rejected">Rejected</option>
                    <option value="waitlisted">Waitlisted</option>
                  </select>
                  <button class="btn btn-primary btn-sm" @click="updateStatus(a)">✓</button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" style="text-align:center;color:#999;padding:30px;">No applications found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const props = defineProps({ driveId: { type: String, required: true } })

const applications = ref([])
const loading = ref(true)
const driveInfo = ref(null)
const search = ref('')
const statusFilter = ref('')

// Filter by search text and status
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return applications.value.filter(a => {
    const matchQ = !q || a.student_name?.toLowerCase().includes(q) || a.student_email?.toLowerCase().includes(q)
    const matchS = !statusFilter.value || a.status === statusFilter.value
    return matchQ && matchS
  })
})

// Load applications and drive info together
onMounted(async () => {
  try {
    const [appRes, driveRes] = await Promise.all([
      api.get(`/company/drives/${props.driveId}/applications`),
      api.get(`/company/drives/${props.driveId}`)
    ])
    applications.value = appRes.data.map(a => ({ ...a, _newStatus: a.status }))
    driveInfo.value = driveRes.data
  } catch (e) {
    showToast('Failed to load', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { applied: 'badge-applied', shortlisted: 'badge-shortlisted', selected: 'badge-approved', rejected: 'badge-rejected', waitlisted: 'badge-pending' }[s] || ''
}

function cgpaBadge(cgpa) {
  return cgpa >= 8 ? 'badge-approved' : cgpa >= 6 ? 'badge-pending' : 'badge-rejected'
}

// Update the application status on the server
async function updateStatus(a) {
  try {
    await api.put(`/company/applications/${a.id}/status`, { status: a._newStatus })
    a.status = a._newStatus
    showToast(`Updated to ${a._newStatus}`)
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed', 'danger')
  }
}
</script>
