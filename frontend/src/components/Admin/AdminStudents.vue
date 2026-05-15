<template>
  <div>
    <h3 style="margin-bottom:16px;">Students</h3>

    <!-- Search -->
    <input class="form-control" style="max-width:260px;margin-bottom:14px;"
      v-model="search" placeholder="Search by name or email..." />

    <!-- Loading -->
    <div v-if="loading" style="text-align:center;padding:40px;">Loading...</div>

    <!-- Table -->
    <div v-else style="overflow-x:auto;">
      <table class="simple-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Branch</th>
            <th>CGPA</th>
            <th>Year</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td>
              <div style="font-weight:600;">{{ s.name }}</div>
              <div style="color:#666;font-size:0.82rem;">{{ s.email }}</div>
            </td>
            <td>{{ s.branch || '—' }}</td>
            <td>
              <span class="badge"
                :class="s.cgpa >= 8 ? 'badge-approved' : s.cgpa >= 6 ? 'badge-pending' : 'badge-rejected'">
                {{ s.cgpa || '—' }}
              </span>
            </td>
            <td>{{ s.year || '—' }}</td>
            <td>
              <span class="badge" :class="s.is_active ? 'badge-approved' : 'badge-rejected'">
                {{ s.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm"
                :style="s.is_active ? 'background:#fff;border:1px solid #ea4335;color:#ea4335;' : 'background:#fff;border:1px solid #34a853;color:#34a853;'"
                @click="toggle(s)">
                {{ s.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="6" style="text-align:center;color:#999;padding:30px;">No students found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { showToast } from '@/api/axios'

const students = ref([])
const loading = ref(true)
const search = ref('')

// Filter by name or email
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return students.value.filter(s => !q || s.name?.toLowerCase().includes(q) || s.email?.toLowerCase().includes(q))
})

onMounted(async () => {
  try {
    const r = await api.get('/admin/students')
    students.value = r.data
  } catch (e) {
    showToast('Failed', 'danger')
  } finally {
    loading.value = false
  }
})

// Toggle student active/inactive
async function toggle(s) {
  try {
    const r = await api.post(`/admin/students/${s.id}/deactivate`)
    s.is_active = r.data.is_active
    showToast(r.data.message)
  } catch (e) { showToast('Failed', 'danger') }
}
</script>
