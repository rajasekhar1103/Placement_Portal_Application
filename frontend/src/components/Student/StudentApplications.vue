<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h3 style="margin:0;">My Applications</h3>
      <button class="btn btn-outline-secondary btn-sm" @click="exportCsv" :disabled="exporting">
        {{ exporting ? 'Exporting...' : '⬇ Export CSV' }}
      </button>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>
    <div v-else>
      <!-- Filter buttons -->
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">
        <button class="btn btn-sm" :style="filter==='' ? 'background:#1a73e8;color:white;' : 'background:#fff;border:1px solid #ccc;'" @click="filter=''">All ({{ applications.length }})</button>
        <button class="btn btn-sm" :style="filter==='applied' ? 'background:#1a73e8;color:white;' : 'background:#fff;border:1px solid #ccc;'" @click="filter='applied'">Applied ({{ count('applied') }})</button>
        <button class="btn btn-sm" :style="filter==='shortlisted' ? 'background:#ff8c00;color:white;' : 'background:#fff;border:1px solid #ccc;'" @click="filter='shortlisted'">Shortlisted ({{ count('shortlisted') }})</button>
        <button class="btn btn-sm" :style="filter==='selected' ? 'background:#34a853;color:white;' : 'background:#fff;border:1px solid #ccc;'" @click="filter='selected'">Selected ({{ count('selected') }})</button>
        <button class="btn btn-sm" :style="filter==='rejected' ? 'background:#ea4335;color:white;' : 'background:#fff;border:1px solid #ccc;'" @click="filter='rejected'">Rejected ({{ count('rejected') }})</button>
      </div>

      <!-- Application cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;">
        <div class="drive-card" v-for="a in filtered" :key="a.id">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
            <div>
              <div style="font-weight:600;">{{ a.job_title }}</div>
              <div style="color:#1a73e8;font-size:0.88rem;">{{ a.company_name }}</div>
            </div>
            <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
          </div>
          <div style="color:#999;font-size:0.82rem;">📅 Applied: {{ new Date(a.application_date).toLocaleDateString('en-IN') }}</div>
          <div v-if="a.remarks" style="color:#666;font-size:0.82rem;margin-top:6px;">💬 {{ a.remarks }}</div>

          <!-- Simple progress bar -->
          <div style="margin-top:12px;">
            <div style="background:#eee;border-radius:10px;height:6px;">
              <div style="background:#1a73e8;border-radius:10px;height:6px;" :style="{ width: progressWidth(a.status) + '%' }"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#999;margin-top:3px;">
              <span>Applied</span><span>Shortlisted</span><span>Selected</span>
            </div>
          </div>
        </div>

        <div v-if="!filtered.length" style="text-align:center;color:#999;padding:30px;grid-column:1/-1;">
          No applications in this category.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const applications = ref([])
const loading = ref(true)
const filter = ref('')
const exporting = ref(false)

// Filter by selected status
const filtered = computed(() => applications.value.filter(a => !filter.value || a.status === filter.value))

onMounted(async () => {
  try {
    const r = await api.get('/student/applications')
    applications.value = r.data
  } catch (e) {
    showToast('Failed to load', 'danger')
  } finally {
    loading.value = false
  }
})

function count(s) { return applications.value.filter(a => a.status === s).length }

function statusBadge(s) {
  return { applied: 'badge-applied', shortlisted: 'badge-shortlisted', selected: 'badge-approved', rejected: 'badge-rejected' }[s] || ''
}

function progressWidth(s) {
  return { applied: 20, shortlisted: 55, selected: 100, rejected: 100 }[s] || 0
}

// Export CSV download
async function exportCsv() {
  exporting.value = true
  try {
    const res = await api.post('/student/export', {}, { responseType: 'blob' })
    const contentType = (res.headers['content-type'] || '').toLowerCase()

    // If backend triggers async job
    if (res.status === 202) {
      showToast('Export started! Email incoming.', 'success')
    }
    // JSON response (probably an error) inside a blob
    else if (contentType.includes('application/json')) {
      const text = await res.data.text()
      let msg = 'Export failed'
      try {
        const obj = JSON.parse(text)
        msg = obj.error || obj.message || text
      } catch {
        msg = text
      }
      showToast(msg, 'danger')
    }
    // Otherwise treat as CSV blob
    else {
      const blob = new Blob([res.data], { type: contentType || 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'my_applications.csv'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      showToast('Downloaded!', 'success')
    }
  } catch (e) {
    showToast('Export failed', 'danger')
  } finally {
    exporting.value = false
  }
}
</script>
