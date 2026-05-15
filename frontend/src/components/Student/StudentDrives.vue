<template>
  <div>
    <h3 style="margin-bottom:16px;">Browse Placement Drives</h3>

    <!-- Filter bar -->
    <div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:14px;margin-bottom:16px;">
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;">
        <div style="flex:1;min-width:180px;">
          <label class="form-label">Search</label>
          <input class="form-control" v-model="search" placeholder="Job title, company, location..." @input="loadDrives" />
        </div>
        <div style="min-width:160px;">
          <label class="form-label">Branch</label>
          <select class="form-select" v-model="branchFilter" @change="loadDrives">
            <option value="">All Branches</option>
            <option>CSE</option><option>ECE</option><option>ME</option>
            <option>EE</option><option>CE</option><option>IT</option>
          </select>
        </div>
        <div style="display:flex;align-items:center;gap:6px;padding-bottom:4px;">
          <input type="checkbox" id="eligibleOnly" v-model="eligibleOnly" @change="loadDrives" />
          <label for="eligibleOnly" style="cursor:pointer;">Eligible only</label>
        </div>
        <button class="btn btn-outline-secondary" @click="reset">Reset</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Drive cards grid -->
    <div v-else style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;">
      <div class="drive-card" v-for="d in drives" :key="d.id" style="display:flex;flex-direction:column;">
        <!-- Title and status -->
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
          <div>
            <div style="font-weight:600;">{{ d.job_title }}</div>
            <div style="color:#1a73e8;font-size:0.88rem;font-weight:600;">{{ d.company_name }}</div>
          </div>
          <span v-if="d.already_applied" class="badge badge-applied">Applied</span>
        </div>
        <!-- Description -->
        <p style="color:#666;font-size:0.85rem;flex:1;margin-bottom:10px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">
          {{ d.job_description || 'No description.' }}
        </p>
        <!-- Tags -->
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px;">
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">📍 {{ d.location || 'Remote' }}</span>
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">💰 {{ d.salary || 'See JD' }}</span>
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">🎓 CGPA {{ d.eligibility_cgpa || 0 }}+</span>
          <span class="badge" style="background:#e8f0fe;color:#1a73e8;">{{ d.interview_type }}</span>
        </div>
        <!-- Footer -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:auto;">
          <span style="color:#999;font-size:0.8rem;">
            {{ d.application_deadline ? 'Due: ' + new Date(d.application_deadline).toLocaleDateString('en-IN') : 'Open' }}
          </span>
          <button v-if="!d.already_applied" class="btn btn-primary btn-sm" @click="apply(d)">Apply Now</button>
          <button v-else class="btn btn-secondary btn-sm" disabled>Applied</button>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!drives.length" style="text-align:center;color:#999;padding:40px;grid-column:1/-1;">
        🔍 No drives found.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const drives = ref([])
const loading = ref(false)
const search = ref('')
const branchFilter = ref('')
const eligibleOnly = ref(false)

onMounted(loadDrives)

// Fetch drives with current filters
async function loadDrives() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      q: search.value,
      branch: branchFilter.value,
      eligible_only: String(eligibleOnly.value)
    })
    const r = await api.get('/student/drives?' + params.toString())
    drives.value = r.data
  } catch (e) {
    showToast('Failed to load drives', 'danger')
  } finally {
    loading.value = false
  }
}

// Apply to a drive
async function apply(d) {
  try {
    await api.post(`/student/drives/${d.id}/apply`)
    showToast('Application submitted!', 'success')
    d.already_applied = true
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to apply', 'danger')
  }
}

// Reset filters and reload
function reset() {
  search.value = ''
  branchFilter.value = ''
  eligibleOnly.value = false
  loadDrives()
}
</script>
