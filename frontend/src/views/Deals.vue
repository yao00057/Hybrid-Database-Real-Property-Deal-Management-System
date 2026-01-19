<template>
  <div class="deals-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Deal Management</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            Create Deal
          </el-button>
        </div>
      </template>

      <el-row :gutter="20" class="filter-row">
        <el-col :span="6">
          <el-select v-model="filterStatus" placeholder="Filter by status" clearable @change="loadDeals">
            <el-option label="Draft" value="draft" />
            <el-option label="Submitted" value="submitted" />
            <el-option label="Conditional" value="conditional" />
            <el-option label="Firm" value="firm" />
            <el-option label="Closing" value="closing" />
            <el-option label="Completed" value="completed" />
            <el-option label="Cancelled" value="cancelled" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="deals" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="_id" label="Deal ID" width="120">
          <template #default="{ row }">
            {{ row._id.substring(0, 8) }}...
          </template>
        </el-table-column>
        <el-table-column label="Property" min-width="200">
          <template #default="{ row }">
            {{ getPropertyAddress(row.property_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="offer_price" label="Offer Price" width="140">
          <template #default="{ row }">
            ${{ row.offer_price.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Buyer" width="150">
          <template #default="{ row }">
            {{ row.participants_snapshot?.buyer?.name || 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column label="Closing Date" width="120">
          <template #default="{ row }">
            {{ row.closing_date ? new Date(row.closing_date).toLocaleDateString() : 'TBD' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDeal(row)">View</el-button>
            <el-button size="small" type="primary" @click="openStatusDialog(row)" :disabled="!canUpdateStatus(row.status)">
              Update
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="loadDeals"
        class="pagination"
      />
    </el-card>

    <!-- Create Deal Dialog -->
    <el-dialog v-model="addDialogVisible" title="Create Deal" width="700">
      <el-form :model="dealForm" :rules="rules" ref="formRef" label-width="130px">
        <el-form-item label="Property" prop="property_id">
          <el-select v-model="dealForm.property_id" placeholder="Select property" style="width: 100%">
            <el-option
              v-for="prop in activeProperties"
              :key="prop._id"
              :label="`${prop.address.street}, ${prop.address.city} - $${prop.listing_price.toLocaleString()}`"
              :value="prop._id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Offer Price" prop="offer_price">
          <el-input-number v-model="dealForm.offer_price" :min="1" :step="10000" style="width: 200px" />
        </el-form-item>
        <el-form-item label="Closing Date">
          <el-date-picker v-model="dealForm.closing_date" type="date" placeholder="Select date" />
        </el-form-item>

        <el-divider>Participants</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Buyer">
              <el-select v-model="dealForm.participants.buyer_id" placeholder="Select buyer" clearable style="width: 100%">
                <el-option v-for="u in buyers" :key="u._id" :label="u.profile.name" :value="u._id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Seller">
              <el-select v-model="dealForm.participants.seller_id" placeholder="Select seller" clearable style="width: 100%">
                <el-option v-for="u in sellers" :key="u._id" :label="u.profile.name" :value="u._id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Buyer Agent">
              <el-select v-model="dealForm.participants.buyer_agent_id" placeholder="Select agent" clearable style="width: 100%">
                <el-option v-for="u in buyerAgents" :key="u._id" :label="u.profile.name" :value="u._id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Seller Agent">
              <el-select v-model="dealForm.participants.seller_agent_id" placeholder="Select agent" clearable style="width: 100%">
                <el-option v-for="u in sellerAgents" :key="u._id" :label="u.profile.name" :value="u._id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Notes">
          <el-input v-model="dealForm.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createDeal" :loading="saving">Create</el-button>
      </template>
    </el-dialog>

    <!-- View Deal Dialog -->
    <el-dialog v-model="viewDialogVisible" title="Deal Details" width="800">
      <template v-if="selectedDeal">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Deal ID">{{ selectedDeal._id }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedDeal.status)">{{ selectedDeal.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Offer Price">${{ selectedDeal.offer_price.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Closing Date">
            {{ selectedDeal.closing_date ? new Date(selectedDeal.closing_date).toLocaleDateString() : 'TBD' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>Participants (Snapshot)</el-divider>
        <el-row :gutter="20">
          <el-col :span="12" v-for="(participant, role) in selectedDeal.participants_snapshot" :key="role">
            <el-card shadow="never" class="participant-card">
              <template #header>{{ formatRole(role as string) }}</template>
              <p><strong>Name:</strong> {{ participant.name }}</p>
              <p><strong>Email:</strong> {{ participant.email }}</p>
              <p v-if="participant.phone"><strong>Phone:</strong> {{ participant.phone }}</p>
              <p v-if="participant.license_number"><strong>License:</strong> {{ participant.license_number }}</p>
            </el-card>
          </el-col>
        </el-row>

        <el-divider>Conditions</el-divider>
        <el-table :data="selectedDeal.conditions" size="small">
          <el-table-column prop="type" label="Type" width="150" />
          <el-table-column prop="description" label="Description" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getConditionStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deadline" label="Deadline" width="120">
            <template #default="{ row }">
              {{ row.deadline ? new Date(row.deadline).toLocaleDateString() : '-' }}
            </template>
          </el-table-column>
        </el-table>

        <el-divider>Status History</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="(entry, index) in selectedDeal.status_history"
            :key="index"
            :timestamp="new Date(entry.timestamp).toLocaleString()"
            :type="getStatusType(entry.status) as any"
          >
            <strong>{{ entry.status }}</strong>
            <p v-if="entry.note">{{ entry.note }}</p>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-dialog>

    <!-- Update Status Dialog -->
    <el-dialog v-model="statusDialogVisible" title="Update Deal Status" width="400">
      <el-form :model="statusForm" label-width="80px">
        <el-form-item label="Status">
          <el-select v-model="statusForm.status" style="width: 100%">
            <el-option
              v-for="status in availableStatuses"
              :key="status"
              :label="status.charAt(0).toUpperCase() + status.slice(1)"
              :value="status"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Note">
          <el-input v-model="statusForm.note" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="updateDealStatus" :loading="saving">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { dealApi, propertyApi, userApi } from '../api/index'
import type { Deal, Property, User } from '../types'

const deals = ref<Deal[]>([])
const activeProperties = ref<Property[]>([])
const buyers = ref<User[]>([])
const sellers = ref<User[]>([])
const buyerAgents = ref<User[]>([])
const sellerAgents = ref<User[]>([])
const propertyMap = ref<Map<string, Property>>(new Map())

const loading = ref(false)
const saving = ref(false)
const addDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const selectedDeal = ref<Deal | null>(null)
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)
const filterStatus = ref('')
const formRef = ref<FormInstance>()

const dealForm = reactive({
  property_id: '',
  offer_price: 0,
  closing_date: '',
  participants: {
    buyer_id: '',
    seller_id: '',
    buyer_agent_id: '',
    seller_agent_id: ''
  },
  notes: ''
})

const statusForm = reactive({
  status: '',
  note: ''
})

const rules: FormRules = {
  property_id: [{ required: true, message: 'Property is required', trigger: 'change' }],
  offer_price: [{ required: true, type: 'number', min: 1, message: 'Valid price required', trigger: 'blur' }]
}

const validTransitions: Record<string, string[]> = {
  draft: ['submitted', 'cancelled'],
  submitted: ['conditional', 'firm', 'cancelled', 'expired'],
  conditional: ['firm', 'cancelled', 'expired'],
  firm: ['closing', 'cancelled'],
  closing: ['completed', 'cancelled'],
  completed: [],
  cancelled: [],
  expired: []
}

const availableStatuses = computed(() => {
  if (!selectedDeal.value) return []
  return validTransitions[selectedDeal.value.status] || []
})

const loadDeals = async () => {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize }
    if (filterStatus.value) params.status = filterStatus.value
    const response = await dealApi.getAll(params)
    deals.value = response.deals
    total.value = response.total
  } catch (error) {
    console.error('Failed to load deals:', error)
  } finally {
    loading.value = false
  }
}

const loadFormData = async () => {
  try {
    const [propsRes, buyersRes, sellersRes, buyerAgentsRes, sellerAgentsRes] = await Promise.all([
      propertyApi.getActive(),
      userApi.getByRole('buyer'),
      userApi.getByRole('seller'),
      userApi.getByRole('buyer_agent'),
      userApi.getByRole('seller_agent')
    ])
    activeProperties.value = propsRes
    buyers.value = buyersRes
    sellers.value = sellersRes
    buyerAgents.value = buyerAgentsRes
    sellerAgents.value = sellerAgentsRes

    // Build property map
    propsRes.forEach(p => propertyMap.value.set(p._id, p))
  } catch (error) {
    console.error('Failed to load form data:', error)
  }
}

const getPropertyAddress = (propertyId: string) => {
  const prop = propertyMap.value.get(propertyId)
  return prop ? `${prop.address.street}, ${prop.address.city}` : propertyId.substring(0, 8) + '...'
}

const openAddDialog = () => {
  resetForm()
  addDialogVisible.value = true
}

const resetForm = () => {
  dealForm.property_id = ''
  dealForm.offer_price = 0
  dealForm.closing_date = ''
  dealForm.participants = { buyer_id: '', seller_id: '', buyer_agent_id: '', seller_agent_id: '' }
  dealForm.notes = ''
}

const createDeal = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const participants: any = {}
      if (dealForm.participants.buyer_id) participants.buyer_id = dealForm.participants.buyer_id
      if (dealForm.participants.seller_id) participants.seller_id = dealForm.participants.seller_id
      if (dealForm.participants.buyer_agent_id) participants.buyer_agent_id = dealForm.participants.buyer_agent_id
      if (dealForm.participants.seller_agent_id) participants.seller_agent_id = dealForm.participants.seller_agent_id

      await dealApi.create({
        property_id: dealForm.property_id,
        offer_price: dealForm.offer_price,
        closing_date: dealForm.closing_date || undefined,
        participants,
        notes: dealForm.notes || undefined
      })
      ElMessage.success('Deal created successfully')
      addDialogVisible.value = false
      loadDeals()
    } catch (error) {
      console.error('Failed to create deal:', error)
    } finally {
      saving.value = false
    }
  })
}

const viewDeal = (deal: Deal) => {
  selectedDeal.value = deal
  viewDialogVisible.value = true
}

const openStatusDialog = (deal: Deal) => {
  selectedDeal.value = deal
  statusForm.status = ''
  statusForm.note = ''
  statusDialogVisible.value = true
}

const updateDealStatus = async () => {
  if (!selectedDeal.value || !statusForm.status) return

  saving.value = true
  try {
    await dealApi.updateStatus(selectedDeal.value._id, statusForm.status, statusForm.note || undefined)
    ElMessage.success('Status updated successfully')
    statusDialogVisible.value = false
    loadDeals()
  } catch (error) {
    console.error('Failed to update status:', error)
  } finally {
    saving.value = false
  }
}

const canUpdateStatus = (status: string) => {
  return (validTransitions[status] || []).length > 0
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    submitted: 'primary',
    conditional: 'warning',
    firm: 'success',
    closing: 'success',
    completed: 'success',
    cancelled: 'danger',
    expired: 'danger'
  }
  return types[status] || 'default'
}

const getConditionStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    satisfied: 'success',
    waived: 'info',
    failed: 'danger'
  }
  return types[status] || 'default'
}

const formatRole = (role: string) => {
  return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

onMounted(() => {
  loadDeals()
  loadFormData()
})
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

.filter-row {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.participant-card {
  margin-bottom: 10px;
}

.participant-card p {
  margin: 5px 0;
  font-size: 13px;
}
</style>
