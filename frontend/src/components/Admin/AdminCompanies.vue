<template>
  <div>
    <h3 style="margin-bottom:10px;">Companies</h3>
    <p style="color:#666;margin-bottom:16px;">Manage company registrations and approvals</p>

    <!-- Filters -->
    <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;">
      <input class="form-control" style="max-width:220px;" v-model="search" placeholder="Search companies..." />
      <select class="form-select" style="max-width:170px;" v-model="statusFilter">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
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
            <th>Company</th>
            <th>Industry</th>
            <th>HR Contact</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filtered" :key="c.id">
            <td>
              <div style="font-weight:600;">{{ c.company_name }}</div>
              <div style="color:#666;font-size:0.82rem;">{{ c.email }}</div>
            </td>
            <td>{{ c.industry || '—' }}</td>
            <td>{{ c.hr_contact || '—' }}</td>
            <td>
              <span class="badge" :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span>
              <span class="badge badge-blacklisted" style="margin-left:5px;" v-if="c.is_blacklisted">Blacklisted</span>
            </td>
            <td>
              <div style="display:flex;gap:5px;flex-wrap:wrap;">
                <button class="btn btn-success btn-sm" @click="approve(c)" v-if="c.approval_status === 'pending'">✓ Approve</button>
                <button class="btn btn-danger btn-sm" @click="reject(c)" v-if="c.approval_status !== 'rejected'">✗ Reject</button>
                <button class="btn btn-sm"
                  :style="c.is_blacklisted ? 'background:#aaa;color:white;' : 'background:#fff;border:1px solid #ea4335;color:#ea4335;'"
                  @click="toggleBlacklist(c)">
                  {{ c.is_blacklisted ? 'Un-blacklist' : 'Blacklist' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="5" style="text-align:center;color:#999;padding:30px;">No companies found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const companies = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')

// Filter companies by search text and status
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return companies.value.filter(c => {
    const matchQ = !q || c.company_name?.toLowerCase().includes(q) || c.email?.toLowerCase().includes(q)
    const matchS = !statusFilter.value || c.approval_status === statusFilter.value
    return matchQ && matchS
  })
})

onMounted(async () => {
  try {
    const r = await api.get('/admin/companies')
    companies.value = r.data
  } catch (e) {
    showToast('Failed to load companies', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected' }[s] || ''
}

async function approve(c) {
  try {
    await api.post(`/admin/companies/${c.id}/approve`)
    c.approval_status = 'approved'
    showToast('Company approved')
  } catch (e) { showToast('Failed', 'danger') }
}

async function reject(c) {
  const reason = prompt('Rejection reason (optional):') || ''
  try {
    await api.post(`/admin/companies/${c.id}/reject`, { reason })
    c.approval_status = 'rejected'
    showToast('Company rejected', 'warning')
  } catch (e) { showToast('Failed', 'danger') }
}

async function toggleBlacklist(c) {
  try {
    const r = await api.post(`/admin/companies/${c.id}/blacklist`)
    c.is_blacklisted = r.data.is_blacklisted
    showToast(r.data.message)
  } catch (e) { showToast('Failed', 'danger') }
}
</script>
