<template>
  <div class="deals-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Deal Management</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            Create Deal
          </el-button>
        </div>
      </template>

      <el-table :data="deals" stripe style="width: 100%">
        <el-table-column prop="id" label="Deal ID" width="180" />
        <el-table-column prop="property_address" label="Property" min-width="200" />
        <el-table-column prop="offer_price" label="Offer Price" width="150">
          <template #default="{ row }">
            ${{ row.offer_price?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="closing_date" label="Closing Date" width="130" />
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDeal(row)">View</el-button>
            <el-button size="small" type="primary" @click="updateStatus(row)">Update</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="Create Deal" width="600">
      <el-form :model="newDeal" label-width="120px">
        <el-form-item label="Property">
          <el-select v-model="newDeal.property_id" placeholder="Select property">
            <el-option 
              v-for="prop in availableProperties" 
              :key="prop.id" 
              :label="prop.address" 
              :value="prop.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Offer Price">
          <el-input-number v-model="newDeal.offer_price" :min="0" :step="10000" />
        </el-form-item>
        <el-form-item label="Closing Date">
          <el-date-picker v-model="newDeal.closing_date" type="date" placeholder="Select date" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createDeal">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Deal {
  id: string
  property_id: string
  property_address: string
  offer_price: number
  status: string
  closing_date: string
}

const deals = ref<Deal[]>([])
const showAddDialog = ref(false)
const availableProperties = ref<{ id: string; address: string }[]>([])

const newDeal = reactive({
  property_id: '',
  offer_price: 0,
  closing_date: ''
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    active: 'primary',
    conditional: 'warning',
    firm: 'success',
    closed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const createDeal = () => {
  ElMessage.success('Deal created successfully')
  showAddDialog.value = false
}

const viewDeal = (_deal: Deal) => {
  ElMessage.info('View feature coming soon')
}

const updateStatus = (_deal: Deal) => {
  ElMessage.info('Status update feature coming soon')
}
</script>

<style scoped>
.deals-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
