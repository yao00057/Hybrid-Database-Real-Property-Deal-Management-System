<template>
  <el-container class="app-container">
    <el-header v-if="isAuthenticated">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
          <span>Real Estate System</span>
        </div>
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          router
          class="header-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item v-if="canManageUsers" index="/users">
            <el-icon><User /></el-icon>
            <span>Users</span>
          </el-menu-item>
          <el-menu-item index="/properties">
            <el-icon><OfficeBuilding /></el-icon>
            <span>Properties</span>
          </el-menu-item>
          <el-menu-item index="/deals">
            <el-icon><Document /></el-icon>
            <span>Deals</span>
          </el-menu-item>
          <el-menu-item index="/transactions">
            <el-icon><Money /></el-icon>
            <span>Transactions</span>
          </el-menu-item>
        </el-menu>
        <div class="user-section">
          <span class="user-name">{{ userName }} ({{ formatRole(userRole) }})</span>
          <el-button type="danger" size="small" @click="handleLogout">Logout</el-button>
        </div>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
    <el-footer v-if="isAuthenticated">
      <span>Real Property Deal Management System - CST8276 Project</span>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, OfficeBuilding, Document, Money, User, DataLine } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isAuthenticated = ref(false)
const userName = ref('')
const userRole = ref('')

const activeIndex = computed(() => route.path)

const canManageUsers = computed(() => {
  return ['buyer_agent', 'seller_agent', 'buyer_lawyer', 'seller_lawyer'].includes(userRole.value)
})

const formatRole = (role: string) => {
  const roleMap: Record<string, string> = {
    buyer: 'Buyer',
    seller: 'Seller',
    buyer_agent: 'Buyer Agent',
    seller_agent: 'Seller Agent',
    buyer_lawyer: 'Buyer Lawyer',
    seller_lawyer: 'Seller Lawyer'
  }
  return roleMap[role] || role
}

const checkAuth = () => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')

  if (token && user) {
    isAuthenticated.value = true
    try {
      const userData = JSON.parse(user)
      userName.value = userData.profile?.name || userData.email
      userRole.value = userData.role || ''
    } catch {
      userName.value = ''
      userRole.value = ''
    }
  } else {
    isAuthenticated.value = false
    userName.value = ''
    userRole.value = ''
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  isAuthenticated.value = false
  userName.value = ''
  userRole.value = ''
  ElMessage.success('Logged out successfully')
  router.push('/login')
}

// Check auth on route change
watch(() => route.path, () => {
  checkAuth()
}, { immediate: true })

onMounted(() => {
  checkAuth()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 40px;
}

.header-menu {
  flex: 1;
  border-bottom: none !important;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  color: #606266;
  font-size: 14px;
}

.el-main {
  background-color: #f5f7fa;
  padding: 0;
}

.el-footer {
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  line-height: 60px;
  color: #909399;
}
</style>
