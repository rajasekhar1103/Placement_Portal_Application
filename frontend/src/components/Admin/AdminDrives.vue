<template>
  <div>
    <h3 style="margin-bottom:10px;">Placement Drives</h3>
    <p style="color:#666;margin-bottom:16px;">Approve, reject or close placement drives</p>

    <!-- Filters -->
    <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;">
      <input class="form-control" style="max-width:220px;" v-model="search" placeholder="Search drives..." />
      <select class="form-select" style="max-width:170px;" v-model="statusFilter">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="closed">Closed</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Table -->
    <div v-else style="overflow-x:auto;">
      <table class="simple-table">
        <thead>
          <tr>
            <th>Drive / Location</th>
            <th>Company</th>
            <th>Salary</th>
            <th>Deadline</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filtered" :key="d.id">
            <td>
              <div style="font-weight:600;">{{ d.job_title }}</div>
              <div style="color:#666;font-size:0.82rem;">{{ d.location || '—' }}</div>
            </td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.salary || '—' }}</td>
            <td>{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString('en-IN') : '—' }}</td>
            <td><span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span></td>
            <td>
              <div style="display:flex;gap:5px;flex-wrap:wrap;">
                <button class="btn btn-success btn-sm" v-if="d.status === 'pending'" @click="approve(d)">✓ Approve</button>
                <button class="btn btn-danger btn-sm" v-if="d.status !== 'rejected'" @click="reject(d)">✗ Reject</button>
                <button class="btn btn-secondary btn-sm" v-if="d.status === 'approved'" @click="close(d)">Close</button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="6" style="text-align:center;color:#999;padding:30px;">No drives found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const drives = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')

// Filter by search text and status
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return drives.value.filter(d => {
    const matchQ = !q || d.job_title?.toLowerCase().includes(q) || d.company_name?.toLowerCase().includes(q)
    const matchS = !statusFilter.value || d.status === statusFilter.value
    return matchQ && matchS
  })
})

onMounted(async () => {
  try {
    const r = await api.get('/admin/drives')
    drives.value = r.data
  } catch (e) {
    showToast('Failed', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected', closed: 'badge-closed' }[s] || ''
}

async function approve(d) {
  try { await api.post(`/admin/drives/${d.id}/approve`); d.status = 'approved'; showToast('Drive approved') }
  catch (e) { showToast('Failed', 'danger') }
}

async function reject(d) {
  const reason = prompt('Rejection reason (optional):') || ''
  try { await api.post(`/admin/drives/${d.id}/reject`, { reason }); d.status = 'rejected'; showToast('Drive rejected', 'warning') }
  catch (e) { showToast('Failed', 'danger') }
}

async function close(d) {
  try { await api.post(`/admin/drives/${d.id}/close`); d.status = 'closed'; showToast('Drive closed') }
  catch (e) { showToast('Failed', 'danger') }
}
</script>
