<template>
  <div>
    <h3 style="margin-bottom:16px;">All Applications</h3>

    <!-- Filters -->
    <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;">
      <input class="form-control" style="max-width:240px;" v-model="search" placeholder="Search student/drive/company..." />
      <select class="form-select" style="max-width:180px;" v-model="statusFilter">
        <option value="">All Statuses</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Table -->
    <div v-else style="overflow-x:auto;">
      <table class="simple-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Drive</th>
            <th>Company</th>
            <th>Applied On</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filtered" :key="a.id">
            <td>
              <div style="font-weight:600;">{{ a.student_name }}</div>
              <div style="color:#666;font-size:0.82rem;">{{ a.student_email }}</div>
            </td>
            <td>{{ a.job_title }}</td>
            <td>{{ a.company_name }}</td>
            <td>{{ a.application_date ? new Date(a.application_date).toLocaleDateString('en-IN') : '—' }}</td>
            <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="5" style="text-align:center;color:#999;padding:30px;">No applications found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const applications = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')

// Filter by text and status
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return applications.value.filter(a => {
    const matchQ = !q || a.student_name?.toLowerCase().includes(q) || a.job_title?.toLowerCase().includes(q) || a.company_name?.toLowerCase().includes(q)
    const matchS = !statusFilter.value || a.status === statusFilter.value
    return matchQ && matchS
  })
})

onMounted(async () => {
  try {
    const r = await api.get('/admin/applications')
    applications.value = r.data
  } catch (e) {
    showToast('Failed', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { applied: 'badge-applied', shortlisted: 'badge-shortlisted', selected: 'badge-approved', rejected: 'badge-rejected' }[s] || ''
}
</script>
