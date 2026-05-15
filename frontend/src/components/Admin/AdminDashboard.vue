<template>
  <div>
    <h3 style="margin-bottom:20px;">Admin Dashboard</h3>

    <!-- Loading spinner -->
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Stats grid -->
    <div v-else-if="data">
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;">
        <div class="stat-card">
          <div class="stat-value">{{ data.total_students }}</div>
          <div class="stat-label">Students</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#fbbc04;">{{ data.total_companies }}</div>
          <div class="stat-label">Companies</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#1a73e8;">{{ data.total_drives }}</div>
          <div class="stat-label">Total Drives</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#34a853;">{{ data.selected_students }}</div>
          <div class="stat-label">Selected</div>
        </div>
      </div>

      <!-- Action cards -->
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
        <div class="stat-card">
          <div class="stat-value" style="color:#ea4335;">{{ data.pending_companies }}</div>
          <div class="stat-label">Pending Companies</div>
          <button class="btn btn-outline-warning btn-sm" style="margin-top:10px;" @click="$router.push('/admin/companies')">Review</button>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#1a73e8;">{{ data.pending_drives }}</div>
          <div class="stat-label">Pending Drives</div>
          <button class="btn btn-outline-primary btn-sm" style="margin-top:10px;" @click="$router.push('/admin/drives')">Review</button>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:#1a73e8;">{{ data.total_applications }}</div>
          <div class="stat-label">Total Applications</div>
          <button class="btn btn-outline-info btn-sm" style="margin-top:10px;" @click="$router.push('/admin/applications')">View All</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const data = ref(null)
const loading = ref(true)

// Load dashboard stats when component mounts
onMounted(async () => {
  try {
    const r = await api.get('/admin/dashboard')
    data.value = r.data
  } catch (e) {
    showToast('Failed to load dashboard', 'danger')
  } finally {
    loading.value = false
  }
})
</script>
