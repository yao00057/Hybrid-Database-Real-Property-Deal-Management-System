<template>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#409EFF"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.users }}</div>
              <div class="stat-label">Total Users</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#67C23A"><OfficeBuilding /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.properties }}</div>
              <div class="stat-label">Properties</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#E6A23C"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.deals }}</div>
              <div class="stat-label">Active Deals</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" color="#F56C6C"><Money /></el-icon>
            <div class="stat-info">
              <div class="stat-number">${{ formatNumber(stats.transactions) }}</div>
              <div class="stat-label">Transaction Value</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Recent Properties</span>
          </template>
          <el-table :data="recentProperties" stripe size="small">
            <el-table-column prop="address.street" label="Address" />
            <el-table-column prop="type" label="Type" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'residential' ? 'success' : 'warning'" size="small">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="listing_price" label="Price" width="120">
              <template #default="{ row }">
                ${{ row.listing_price?.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Recent Deals</span>
          </template>
          <el-table :data="recentDeals" stripe size="small">
            <el-table-column prop="deal_name" label="Deal" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getDealStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deal_price" label="Price" width="120">
              <template #default="{ row }">
                ${{ row.deal_price?.toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, OfficeBuilding, Document, Money } from '@element-plus/icons-vue'
import { dashboardApi, propertiesApi, dealsApi } from '../api'

const stats = ref({
  users: 0,
  properties: 0,
  deals: 0,
  transactions: 0
})

const recentProperties = ref([])
const recentDeals = ref([])

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    pending: 'warning',
    sold: 'info',
    withdrawn: 'danger'
  }
  return types[status] || 'info'
}

const getDealStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    active: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const loadDashboard = async () => {
  try {
    const [statsRes, propsRes, dealsRes] = await Promise.all([
      dashboardApi.getStats(),
      propertiesApi.getAll({ limit: 5 }),
      dealsApi.getAll({ limit: 5 })
    ])

    stats.value = statsRes.data
    recentProperties.value = propsRes.data.slice(0, 5)
    recentDeals.value = dealsRes.data.slice(0, 5)
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
}

onMounted(() => loadDashboard())
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard h1 {
  margin-bottom: 20px;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 100%;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}
</style>
