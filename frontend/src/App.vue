<template>
  <div>
    <!-- Toast notifications -->
    <div class="toast-container">
      <div
        v-for="t in toastState.messages"
        :key="t.id"
        class="toast"
        :class="`text-bg-${t.type}`"
        role="alert"
      >
        <span>{{ t.message }}</span>
        <button
          type="button"
          style="background:none;border:none;cursor:pointer;font-size:1rem;color:inherit;margin-left:10px;"
          @click="dismiss(t.id)"
        >✕</button>
      </div>
    </div>

    <!-- Login / Register page (no sidebar) -->
    <template v-if="!authState.isLoggedIn">
      <router-view />
    </template>

    <!-- Dashboard layout: Navbar + Sidebar + Content -->
    <template v-else>
      <!-- Top Navbar -->
      <nav class="navbar-custom">
        <a class="navbar-brand">🎓 PlacementPortal</a>
        <!-- Hamburger for mobile -->
        <button
          style="background:none;border:1px solid white;color:white;padding:5px 10px;border-radius:5px;cursor:pointer;display:none"
          class="sidebar-toggle"
          type="button"
          @click="sidebarOpen = !sidebarOpen"
        >☰</button>
        <!-- Right side: role badge + email + logout -->
        <div style="display:flex;align-items:center;gap:14px;">
          <span class="badge" :class="roleBadge" style="font-size:0.85rem;padding:5px 12px;">
            {{ authState.role?.toUpperCase() }}
          </span>
          <span style="color:#dce6ff;font-size:0.85rem;display:none" class="d-md-inline">
            {{ authState.user?.email }}
          </span>
          <button class="btn btn-outline-danger btn-sm" @click="logout"
            style="background:transparent;border:1px solid #ff8a80;color:#ff8a80;">
            Logout
          </button>
        </div>
      </nav>

      <div style="display:flex;">
        <!-- Sidebar -->
        <nav class="sidebar" :class="{ show: sidebarOpen }">
          <!-- Admin links -->
          <ul style="list-style:none;padding:0;margin:0;" v-if="authState.isAdmin">
            <li><a class="nav-link" :class="{ active: $route.path === '/admin' || $route.path === '/admin/' }" href="#" @click.prevent="nav('/admin')">🏠 Dashboard</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/admin/companies') }" href="#" @click.prevent="nav('/admin/companies')">🏢 Companies</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/admin/students') }" href="#" @click.prevent="nav('/admin/students')">🎓 Students</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/admin/drives') }" href="#" @click.prevent="nav('/admin/drives')">💼 Drives</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/admin/applications') }" href="#" @click.prevent="nav('/admin/applications')">📄 Applications</a></li>
          </ul>
          <!-- Company links -->
          <ul style="list-style:none;padding:0;margin:0;" v-if="authState.isCompany">
            <li><a class="nav-link" :class="{ active: $route.path === '/company' || $route.path === '/company/' }" href="#" @click.prevent="nav('/company')">🏠 Dashboard</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.startsWith('/company/drives') }" href="#" @click.prevent="nav('/company/drives')">💼 My Drives</a></li>
            <li><a class="nav-link" href="#" @click.prevent="nav('/company/drives/create')">➕ Create Drive</a></li>
          </ul>
          <!-- Student links -->
          <ul style="list-style:none;padding:0;margin:0;" v-if="authState.isStudent">
            <li><a class="nav-link" :class="{ active: $route.path === '/student' || $route.path === '/student/' }" href="#" @click.prevent="nav('/student')">🏠 Dashboard</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/student/drives') }" href="#" @click.prevent="nav('/student/drives')">💼 Browse Drives</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/student/applications') }" href="#" @click.prevent="nav('/student/applications')">📄 My Applications</a></li>
            <li><a class="nav-link" :class="{ active: $route.path.includes('/student/profile') }" href="#" @click.prevent="nav('/student/profile')">👤 Profile</a></li>
          </ul>
        </nav>

        <!-- Main content -->
        <main class="main-content" style="flex:1;">
          <router-view />
        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authState, toastState } from '@/api/axios'

const router = useRouter()
const sidebarOpen = ref(false)

// Badge colour per role
const roleBadge = computed(() => ({
  admin: 'badge-rejected',
  company: 'badge-pending',
  student: 'badge-applied'
}[authState.role] || 'bg-secondary'))

// Navigate and close sidebar on mobile
function nav(path) {
  router.push(path)
  sidebarOpen.value = false
}

// Log out and go to login
function logout() {
  authState.logout()
  router.push('/')
}

// Dismiss a toast by its id
function dismiss(id) {
  toastState.messages = toastState.messages.filter(m => m.id !== id)
}
</script>
