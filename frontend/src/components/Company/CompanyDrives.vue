<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h3 style="margin:0;">My Drives</h3>
      <button class="btn btn-primary btn-sm" @click="$router.push('/company/drives/create')">➕ New Drive</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Drive cards -->
    <div v-else style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;">
      <div class="drive-card" v-for="d in drives" :key="d.id" style="display:flex;flex-direction:column;">
        <!-- Header -->
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
          <div>
            <div style="font-weight:600;font-size:1rem;">{{ d.job_title }}</div>
            <div style="color:#666;font-size:0.85rem;">{{ d.location || '—' }} · {{ d.salary || 'CTC N/A' }}</div>
          </div>
          <span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span>
        </div>
        <!-- Description -->
        <p style="color:#666;font-size:0.85rem;flex:1;margin-bottom:10px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">
          {{ d.job_description || 'No description.' }}
        </p>
        <!-- Tags -->
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px;">
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">CGPA {{ d.eligibility_cgpa || 0 }}+</span>
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">{{ d.eligibility_branch || 'All' }}</span>
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">{{ d.interview_type }}</span>
        </div>
        <!-- View applicants button -->
        <button class="btn btn-outline-primary btn-sm"
          @click="$router.push(`/company/drives/${d.id}/applications`)">
          👥 {{ d.applicant_count || 0 }} Applicants
        </button>
      </div>

      <!-- Empty state -->
      <div v-if="!drives.length" style="text-align:center;color:#999;padding:40px;grid-column:1/-1;">
        💼 No drives yet. Create one!
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const drives = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const r = await api.get('/company/drives')
    drives.value = r.data
  } catch (e) {
    showToast('Failed to load drives', 'danger')
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected', closed: 'badge-closed' }[s] || ''
}
</script>
