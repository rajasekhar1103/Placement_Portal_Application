<template>
  <div>
    <!-- Welcome header -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;" v-if="student">
      <div>
        <h3 style="margin:0;">Welcome, {{ student.name }} 👋</h3>
        <p style="color:#666;margin:4px 0 0;">{{ student.branch }} · CGPA: {{ student.cgpa }} · Year {{ student.year }}</p>
      </div>
      <button class="btn btn-outline-info btn-sm" @click="$router.push('/student/profile')">👤 Edit Profile</button>
    </div>

    <!-- Stat boxes -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;">
      <div class="stat-card">
        <div class="stat-value" style="color:#1a73e8;">{{ stats.total }}</div>
        <div class="stat-label">Applied</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:#ff8c00;">{{ stats.shortlisted }}</div>
        <div class="stat-label">Shortlisted</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:#34a853;">{{ stats.selected }}</div>
        <div class="stat-label">Selected</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:#ea4335;">{{ stats.rejected }}</div>
        <div class="stat-label">Rejected</div>
      </div>
    </div>

    <!-- Quick actions -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px;">
      <div class="drive-card" style="text-align:center;cursor:pointer;" @click="$router.push('/student/drives')">
        <div style="font-size:2rem;">💼</div>
        <div style="font-weight:600;margin-top:6px;">Browse Drives</div>
        <div style="color:#666;font-size:0.85rem;">Find your next opportunity</div>
      </div>
      <div class="drive-card" style="text-align:center;cursor:pointer;" @click="$router.push('/student/applications')">
        <div style="font-size:2rem;">📄</div>
        <div style="font-weight:600;margin-top:6px;">My Applications</div>
        <div style="color:#666;font-size:0.85rem;">Track your status</div>
      </div>
      <div class="drive-card" style="text-align:center;cursor:pointer;" @click="exportCsv">
        <div style="font-size:2rem;">⬇️</div>
        <div style="font-weight:600;margin-top:6px;">Export History</div>
        <div style="color:#666;font-size:0.85rem;">{{ exporting ? 'Processing...' : 'Download CSV' }}</div>
      </div>
    </div>

    <!-- Recent applications -->
    <h4 style="margin-bottom:14px;">Recent Applications</h4>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;">
      <div class="drive-card" v-for="a in recentApps" :key="a.id">
        <div style="display:flex;justify-content:space-between;align-items:start;">
          <div>
            <div style="font-weight:600;">{{ a.job_title }}</div>
            <div style="color:#666;font-size:0.85rem;">{{ a.company_name }}</div>
          </div>
          <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
        </div>
        <div style="color:#999;font-size:0.82rem;margin-top:8px;">
          Applied: {{ new Date(a.application_date).toLocaleDateString('en-IN') }}
        </div>
      </div>
      <div v-if="!recentApps.length && !loadingApps" style="text-align:center;color:#999;padding:20px;grid-column:1/-1;">
        No applications yet.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const student = ref(null)
const applications = ref([])
const loadingApps = ref(true)
const exporting = ref(false)

// Show only the 4 most recent applications
const recentApps = computed(() => applications.value.slice(0, 4))

// Count stats from application list
const stats = computed(() => ({
  total: applications.value.length,
  shortlisted: applications.value.filter(a => a.status === 'shortlisted').length,
  selected: applications.value.filter(a => a.status === 'selected').length,
  rejected: applications.value.filter(a => a.status === 'rejected').length
}))

// Load profile and applications in parallel
onMounted(async () => {
  try {
    const [profileRes, appsRes] = await Promise.all([
      api.get('/student/profile'),
      api.get('/student/applications')
    ])
    student.value = profileRes.data
    applications.value = appsRes.data
  } catch (e) {
    showToast('Failed to load dashboard', 'danger')
  } finally {
    loadingApps.value = false
  }
})

function statusBadge(s) {
  return { applied: 'badge-applied', shortlisted: 'badge-shortlisted', selected: 'badge-approved', rejected: 'badge-rejected' }[s] || ''
}

// Export applications to CSV — generate entirely on the client side
function exportCsv() {
  exporting.value = true
  try {
    const rows = [
      ['Application ID', 'Company Name', 'Job Title', 'Application Date', 'Status']
    ]
    for (const a of applications.value) {
      rows.push([
        a.id,
        a.company_name || '',
        a.job_title || '',
        a.application_date ? new Date(a.application_date).toLocaleDateString('en-IN') : '',
        a.status || ''
      ])
    }
    // Build CSV string
    const csvContent = rows.map(row =>
      row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ).join('\n')

    // Create a Blob and use a download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.setAttribute('download', `applications_${new Date().toISOString().slice(0,10)}.csv`)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    // Clean up after a short delay
    setTimeout(() => {
      document.body.removeChild(link)
      URL.revokeObjectURL(link.href)
    }, 100)
    showToast('CSV downloaded!', 'success')
  } catch (e) {
    showToast('Export failed', 'danger')
  } finally {
    exporting.value = false
  }
}
</script>
