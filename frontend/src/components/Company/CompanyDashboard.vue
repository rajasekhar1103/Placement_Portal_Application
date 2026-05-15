<template>
  <div>
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>
    <div v-else-if="data">
      <!-- Company info box -->
      <div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:18px;margin-bottom:18px;">
        <div style="display:flex;justify-content:space-between;align-items:start;">
          <div>
            <h3 style="margin:0 0 4px;">{{ data.company.company_name }}</h3>
            <p style="color:#666;margin:0;">{{ data.company.industry || 'Technology' }}</p>
          </div>
          <div>
            <span class="badge" :class="statusBadge(data.company.approval_status)">{{ data.company.approval_status }}</span>
            <span v-if="data.company.is_blacklisted" class="badge badge-blacklisted" style="margin-left:6px;">Blacklisted</span>
          </div>
        </div>
        <!-- Pending warning -->
        <div v-if="data.company.approval_status === 'pending'"
          style="background:#fff8e1;border:1px solid #fbbc04;border-radius:6px;padding:10px;margin-top:12px;color:#856404;font-size:0.88rem;">
          ⏳ Your account is pending admin approval. You can create drives after approval.
        </div>
      </div>

      <!-- Stat boxes -->
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;">
        <div class="stat-card">
          <div class="stat-value">{{ data.stats.total_drives }}</div>
          <div class="stat-label">Total Drives</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#1a73e8;">{{ data.stats.total_applicants }}</div>
          <div class="stat-label">Applicants</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#34a853;">{{ selectedCount }}</div>
          <div class="stat-label">Selected</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#fbbc04;">{{ pendingDrives }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </div>

      <!-- Drives list -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h4 style="margin:0;">Your Drives</h4>
        <button class="btn btn-primary btn-sm" @click="$router.push('/company/drives/create')"
          v-if="data.company.approval_status === 'approved'">➕ Create Drive</button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;">
        <div class="drive-card" v-for="d in data.drives.slice(0, 4)" :key="d.id">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
            <div>
              <div style="font-weight:600;">{{ d.job_title }}</div>
              <div style="color:#666;font-size:0.85rem;">{{ d.location }}</div>
            </div>
            <span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span>
          </div>
          <button class="btn btn-outline-primary btn-sm" style="width:100%;"
            @click="$router.push(`/company/drives/${d.id}/applications`)">
            👥 View Applications
          </button>
        </div>
        <div v-if="!data.drives?.length" style="text-align:center;color:#999;padding:30px;grid-column:1/-1;">
          No drives yet.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const data = ref(null)
const loading = ref(true)

// Count selected students across all drives
const selectedCount = computed(() =>
  data.value?.drives?.reduce((t, d) => t + (d.application_counts?.selected || 0), 0) || 0
)

// Count drives with pending status
const pendingDrives = computed(() =>
  data.value?.drives?.filter(d => d.status === 'pending').length || 0
)

onMounted(async () => {
  try {
    const r = await api.get('/company/dashboard')
    data.value = r.data
  } catch (e) {
    showToast('Failed to load dashboard', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected', closed: 'badge-closed' }[s] || ''
}
</script>
