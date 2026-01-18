<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon><HomeFilled /></el-icon>
          <span>Real Property Deal Management System</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="Active Properties" :value="stats.properties" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Ongoing Deals" :value="stats.deals" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Total Users" :value="stats.users" />
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/properties')">
          <el-icon :size="40"><OfficeBuilding /></el-icon>
          <h3>Properties</h3>
          <p>Manage residential and commercial properties</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/deals')">
          <el-icon :size="40"><Document /></el-icon>
          <h3>Deals</h3>
          <p>Track deal lifecycle and conditions</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-icon :size="40"><Money /></el-icon>
          <h3>Transactions</h3>
          <p>Financial tracking and audit logs</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { HomeFilled, OfficeBuilding, Document, Money } from '@element-plus/icons-vue'

const stats = reactive({
  properties: 0,
  deals: 0,
  users: 0
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.feature-cards .el-card {
  text-align: center;
  cursor: pointer;
  padding: 20px;
}

.feature-cards h3 {
  margin: 15px 0 10px;
}

.feature-cards p {
  color: #666;
  font-size: 14px;
}
</style>
