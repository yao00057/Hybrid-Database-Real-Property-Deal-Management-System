<template>
  <div class="properties-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Property Management</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            Add Property
          </el-button>
        </div>
      </template>

      <el-table :data="properties" stripe style="width: 100%">
        <el-table-column prop="type" label="Type" width="120" />
        <el-table-column label="Address" min-width="200">
          <template #default="{ row }">
            {{ row.address?.street }}, {{ row.address?.city }}
          </template>
        </el-table-column>
        <el-table-column prop="listing_price" label="Price" width="150">
          <template #default="{ row }">
            ${{ row.listing_price?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editProperty(row)">Edit</el-button>
            <el-button size="small" type="danger" @click="deleteProperty(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="Add Property" width="500">
      <el-form :model="newProperty" label-width="100px">
        <el-form-item label="Type">
          <el-select v-model="newProperty.type" placeholder="Select type">
            <el-option label="Residential" value="residential" />
            <el-option label="Commercial" value="commercial" />
          </el-select>
        </el-form-item>
        <el-form-item label="Street">
          <el-input v-model="newProperty.address.street" />
        </el-form-item>
        <el-form-item label="City">
          <el-input v-model="newProperty.address.city" />
        </el-form-item>
        <el-form-item label="Price">
          <el-input-number v-model="newProperty.listing_price" :min="0" :step="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">Cancel</el-button>
        <el-button type="primary" @click="addProperty">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Property {
  id?: string
  type: string
  address: {
    street: string
    city: string
  }
  listing_price: number
  status: string
}

const properties = ref<Property[]>([])
const showAddDialog = ref(false)

const newProperty = reactive<Property>({
  type: 'residential',
  address: { street: '', city: '' },
  listing_price: 0,
  status: 'active'
})

const addProperty = () => {
  // TODO: API call to create property
  ElMessage.success('Property added successfully')
  showAddDialog.value = false
}

const editProperty = (_property: Property) => {
  ElMessage.info('Edit feature coming soon')
}

const deleteProperty = (_property: Property) => {
  ElMessage.warning('Delete feature coming soon')
}
</script>

<style scoped>
.properties-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
