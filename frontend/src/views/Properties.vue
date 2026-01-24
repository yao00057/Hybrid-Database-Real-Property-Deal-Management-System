<template>
  <div class="properties-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Property Management</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            Add Property
          </el-button>
        </div>
      </template>

      <el-row :gutter="20" class="filter-row">
        <el-col :span="4">
          <el-select v-model="filters.type" placeholder="Type" clearable @change="loadProperties">
            <el-option label="Residential" value="residential" />
            <el-option label="Commercial" value="commercial" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="Status" clearable @change="loadProperties">
            <el-option label="Active" value="active" />
            <el-option label="Pending" value="pending" />
            <el-option label="Sold" value="sold" />
            <el-option label="Withdrawn" value="withdrawn" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input v-model="filters.city" placeholder="City" clearable @change="loadProperties" />
        </el-col>
        <el-col :span="4">
          <el-input-number v-model="filters.min_price" placeholder="Min Price" :min="0" :step="50000" controls-position="right" style="width: 100%" />
        </el-col>
        <el-col :span="4">
          <el-input-number v-model="filters.max_price" placeholder="Max Price" :min="0" :step="50000" controls-position="right" style="width: 100%" />
        </el-col>
        <el-col :span="4">
          <el-button @click="loadProperties">Search</el-button>
        </el-col>
      </el-row>

      <el-table :data="properties" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'residential' ? 'primary' : 'warning'">
              {{ row.type.charAt(0).toUpperCase() + row.type.slice(1) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Address" min-width="250">
          <template #default="{ row }">
            {{ row.address.street }}, {{ row.address.city }}, {{ row.address.province }}
          </template>
        </el-table-column>
        <el-table-column prop="listing_price" label="Price" width="150">
          <template #default="{ row }">
            ${{ row.listing_price.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="Details" width="150">
          <template #default="{ row }">
            <span v-if="row.type === 'residential'">
              {{ row.attributes.bedrooms || 0 }} bed, {{ row.attributes.bathrooms || 0 }} bath
            </span>
            <span v-else>{{ row.attributes.sqft?.toLocaleString() || 0 }} sqft</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editProperty(row)">Edit</el-button>
            <el-button size="small" type="danger" @click="confirmDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="loadProperties"
        class="pagination"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Property' : 'Add Property'" width="600">
      <el-form :model="propertyForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Type" prop="type">
          <el-select v-model="propertyForm.type" :disabled="isEdit" style="width: 100%">
            <el-option label="Residential" value="residential" />
            <el-option label="Commercial" value="commercial" />
          </el-select>
        </el-form-item>

        <el-divider>Address</el-divider>
        <el-form-item label="Street" prop="address.street">
          <el-input v-model="propertyForm.address.street" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="City" prop="address.city">
              <el-input v-model="propertyForm.address.city" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Province">
              <el-input v-model="propertyForm.address.province" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Postal Code" prop="address.postal_code">
          <el-input v-model="propertyForm.address.postal_code" style="width: 200px" />
        </el-form-item>

        <el-divider>Details</el-divider>
        <el-form-item label="Listing Price" prop="listing_price">
          <el-input-number v-model="propertyForm.listing_price" :min="1" :step="10000" style="width: 200px" />
        </el-form-item>

        <template v-if="propertyForm.type === 'residential'">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Bedrooms">
                <el-input-number v-model="propertyForm.attributes.bedrooms" :min="0" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Bathrooms">
                <el-input-number v-model="propertyForm.attributes.bathrooms" :min="0" :step="0.5" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Sqft">
                <el-input-number v-model="propertyForm.attributes.sqft" :min="0" :step="100" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="Year Built">
            <el-input-number v-model="propertyForm.attributes.year_built" :min="1800" :max="2030" />
          </el-form-item>
        </template>

        <template v-if="propertyForm.type === 'commercial'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Sqft">
                <el-input-number v-model="propertyForm.attributes.sqft" :min="0" :step="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Zoning">
                <el-input v-model="propertyForm.attributes.zoning" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="Cap Rate (%)">
            <el-input-number v-model="propertyForm.attributes.cap_rate" :min="0" :max="100" :step="0.5" />
          </el-form-item>
        </template>

        <el-form-item label="Description">
          <el-input v-model="propertyForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="Status" v-if="isEdit">
          <el-select v-model="propertyForm.status" style="width: 200px">
            <el-option label="Active" value="active" />
            <el-option label="Pending" value="pending" />
            <el-option label="Sold" value="sold" />
            <el-option label="Withdrawn" value="withdrawn" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveProperty" :loading="saving">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { propertiesApi } from '../api/index'
import type { Property } from '../types'

const properties = ref<Property[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)
const formRef = ref<FormInstance>()

const filters = reactive({
  type: '',
  status: '',
  city: '',
  min_price: undefined as number | undefined,
  max_price: undefined as number | undefined
})

const propertyForm = reactive({
  type: 'residential' as string,
  address: {
    street: '',
    city: '',
    province: 'ON',
    postal_code: '',
    country: 'Canada'
  },
  listing_price: 0,
  status: 'active',
  attributes: {} as Record<string, any>,
  description: ''
})

const rules: FormRules = {
  type: [{ required: true, message: 'Type is required', trigger: 'change' }],
  'address.street': [{ required: true, message: 'Street is required', trigger: 'blur' }],
  'address.city': [{ required: true, message: 'City is required', trigger: 'blur' }],
  'address.postal_code': [{ required: true, message: 'Postal code is required', trigger: 'blur' }],
  listing_price: [{ required: true, type: 'number', min: 1, message: 'Valid price required', trigger: 'blur' }]
}

const loadProperties = async () => {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize }
    if (filters.type) params.type = filters.type
    if (filters.status) params.status = filters.status
    if (filters.city) params.city = filters.city
    if (filters.min_price) params.min_price = filters.min_price
    if (filters.max_price) params.max_price = filters.max_price

    const response = await propertiesApi.getAll(params)
    properties.value = response.properties
    total.value = response.total
  } catch (error) {
    console.error('Failed to load properties:', error)
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editProperty = (property: Property) => {
  isEdit.value = true
  editingId.value = property._id
  propertyForm.type = property.type
  propertyForm.address = { ...property.address }
  propertyForm.listing_price = property.listing_price
  propertyForm.status = property.status
  propertyForm.attributes = { ...property.attributes }
  propertyForm.description = property.description || ''
  dialogVisible.value = true
}

const resetForm = () => {
  propertyForm.type = 'residential'
  propertyForm.address = { street: '', city: '', province: 'ON', postal_code: '', country: 'Canada' }
  propertyForm.listing_price = 0
  propertyForm.status = 'active'
  propertyForm.attributes = {}
  propertyForm.description = ''
}

const saveProperty = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      if (isEdit.value) {
        await propertiesApi.update(editingId.value, {
          listing_price: propertyForm.listing_price,
          status: propertyForm.status as any,
          attributes: propertyForm.attributes,
          description: propertyForm.description
        })
        ElMessage.success('Property updated successfully')
      } else {
        await propertiesApi.create({
          type: propertyForm.type as any,
          address: propertyForm.address,
          listing_price: propertyForm.listing_price,
          attributes: propertyForm.attributes,
          description: propertyForm.description
        })
        ElMessage.success('Property created successfully')
      }
      dialogVisible.value = false
      loadProperties()
    } catch (error) {
      console.error('Failed to save property:', error)
    } finally {
      saving.value = false
    }
  })
}

const confirmDelete = (property: Property) => {
  ElMessageBox.confirm(
    `Are you sure you want to delete this property at ${property.address.street}?`,
    'Confirm Delete',
    { type: 'warning' }
  ).then(async () => {
    try {
      await propertiesApi.delete(property._id)
      ElMessage.success('Property deleted')
      loadProperties()
    } catch (error) {
      console.error('Failed to delete property:', error)
    }
  }).catch(() => {})
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    pending: 'warning',
    sold: 'info',
    withdrawn: 'danger'
  }
  return types[status] || 'default'
}

onMounted(() => {
  loadProperties()
})
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

.filter-row {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
