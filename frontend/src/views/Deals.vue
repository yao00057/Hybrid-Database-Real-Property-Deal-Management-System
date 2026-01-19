<template>
  <div class="deals">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Deal Management</span>
          <el-button type="primary" @click="openCreateDialog">Create Deal</el-button>
        </div>
      </template>

      <el-row :gutter="10" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="Status" clearable @change="loadDeals">
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

      <el-table :data="deals" stripe v-loading="loading">
        <el-table-column prop="id" label="Deal ID" width="220" />
        <el-table-column prop="status" label="Status">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="offer_price" label="Offer Price">
          <template #default="{ row }">
            ${{ row.offer_price?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="Participants">
          <template #default="{ row }">
            {{ Object.keys(row.participants_snapshot || {}).length || 0 }} participants
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="viewDeal(row)">View</el-button>
            <el-button size="small" type="primary" @click="updateStatus(row)">Update</el-button>
            <el-button size="small" type="danger" @click="deleteDeal(row.id)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="Create Deal" width="700px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="Property" required>
          <el-select v-model="form.property_id" placeholder="Select a property" style="width: 100%" filterable>
            <el-option
              v-for="prop in properties"
              :key="prop.id"
              :label="formatPropertyLabel(prop)"
              :value="prop.id"
            />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">Participants</el-divider>

        <el-form-item label="Buyer">
          <el-select v-model="form.participants.buyer_id" placeholder="Select buyer" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in buyers"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Seller">
          <el-select v-model="form.participants.seller_id" placeholder="Select seller" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in sellers"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Buyer Agent">
          <el-select v-model="form.participants.buyer_agent_id" placeholder="Select buyer agent" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in buyerAgents"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Seller Agent">
          <el-select v-model="form.participants.seller_agent_id" placeholder="Select seller agent" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in sellerAgents"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Buyer Lawyer">
          <el-select v-model="form.participants.buyer_lawyer_id" placeholder="Select buyer lawyer" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in buyerLawyers"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Seller Lawyer">
          <el-select v-model="form.participants.seller_lawyer_id" placeholder="Select seller lawyer" style="width: 100%" filterable clearable>
            <el-option
              v-for="user in sellerLawyers"
              :key="user.id"
              :label="formatUserLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">Deal Details</el-divider>

        <el-form-item label="Offer Price" required>
          <el-input-number v-model="form.offer_price" :min="0" :step="10000" style="width: 100%" />
        </el-form-item>

        <el-form-item label="Closing Date">
          <el-date-picker v-model="form.closing_date" type="date" placeholder="Select closing date" style="width: 100%" />
        </el-form-item>

        <el-form-item label="Notes">
          <el-input v-model="form.notes" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveDeal" :disabled="!form.property_id || !form.offer_price">Create</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="Deal Details" width="700px">
      <div v-if="selectedDeal">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Deal ID">{{ selectedDeal.id }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedDeal.status)">{{ selectedDeal.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Offer">${{ selectedDeal.offer_price?.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Closing Date">{{ selectedDeal.closing_date || 'Not set' }}</el-descriptions-item>
        </el-descriptions>

        <h4>Participants</h4>
        <el-table :data="getParticipantsList(selectedDeal)" stripe size="small">
          <el-table-column prop="role" label="Role" width="150" />
          <el-table-column prop="name" label="Name" />
          <el-table-column prop="email" label="Email" />
        </el-table>

        <h4 v-if="selectedDeal.conditions?.length">Conditions</h4>
        <el-table v-if="selectedDeal.conditions?.length" :data="selectedDeal.conditions" stripe size="small">
          <el-table-column prop="type" label="Type" width="120" />
          <el-table-column prop="description" label="Description" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'satisfied' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <h4>Status History</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(entry, index) in selectedDeal.status_history"
            :key="index"
            :timestamp="formatDate(entry.timestamp)"
          >
            {{ entry.status }} {{ entry.note ? '- ' + entry.note : '' }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>

    <el-dialog v-model="showStatusDialog" title="Update Status" width="400px">
      <el-select v-model="newStatus" placeholder="Select new status" style="width: 100%">
        <el-option label="Submitted" value="submitted" />
        <el-option label="Conditional" value="conditional" />
        <el-option label="Firm" value="firm" />
        <el-option label="Closing" value="closing" />
        <el-option label="Completed" value="completed" />
        <el-option label="Cancelled" value="cancelled" />
      </el-select>
      <el-input v-model="statusNote" placeholder="Status note (optional)" style="margin-top: 10px" />
      <template #footer>
        <el-button @click="showStatusDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmStatusUpdate" :disabled="!newStatus">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { dealsApi, propertiesApi, usersApi } from "../api"
import type { Deal, Property, User } from "../types"

interface DealForm {
  property_id: string
  offer_price: number
  closing_date: string | null
  notes: string
  participants: {
    buyer_id: string
    seller_id: string
    buyer_agent_id: string
    seller_agent_id: string
    buyer_lawyer_id: string
    seller_lawyer_id: string
  }
  conditions: any[]
}

const deals = ref<Deal[]>([])
const properties = ref<Property[]>([])
const allUsers = ref<User[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showStatusDialog = ref(false)
const selectedDeal = ref<Deal | null>(null)
const newStatus = ref("")
const statusNote = ref("")
const filters = ref({ status: "" })

const form = ref<DealForm>({
  property_id: "",
  offer_price: 0,
  closing_date: null,
  notes: "",
  participants: {
    buyer_id: "",
    seller_id: "",
    buyer_agent_id: "",
    seller_agent_id: "",
    buyer_lawyer_id: "",
    seller_lawyer_id: ""
  },
  conditions: []
})

// Filter users by role
const buyers = computed(() => allUsers.value.filter(u => u.role === "buyer"))
const sellers = computed(() => allUsers.value.filter(u => u.role === "seller"))
const buyerAgents = computed(() => allUsers.value.filter(u => u.role === "buyer_agent"))
const sellerAgents = computed(() => allUsers.value.filter(u => u.role === "seller_agent"))
const buyerLawyers = computed(() => allUsers.value.filter(u => u.role === "buyer_lawyer"))
const sellerLawyers = computed(() => allUsers.value.filter(u => u.role === "seller_lawyer"))

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: "info", submitted: "warning", conditional: "warning",
    firm: "success", closing: "primary", completed: "success",
    cancelled: "danger", expired: "danger"
  }
  return types[status] || "info"
}

const formatPropertyLabel = (prop: Property) => {
  const address = prop.address
  return `${address?.street || 'Unknown'}, ${address?.city || ''} - $${prop.listing_price?.toLocaleString() || 0}`
}

const formatUserLabel = (user: User) => {
  return `${user.profile?.name || user.email} (${user.role})`
}

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const getParticipantsList = (deal: Deal) => {
  const snapshot = deal.participants_snapshot || {}
  return Object.entries(snapshot).map(([role, data]: [string, any]) => ({
    role: role.replace(/_/g, ' '),
    name: data?.name || 'Unknown',
    email: data?.email || ''
  }))
}

const loadDeals = async () => {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.value.status) params.status = filters.value.status
    const response = await dealsApi.getAll(params)
    deals.value = response.data.deals || response.data
  } catch (err) {
    console.error('Failed to load deals:', err)
    ElMessage.error("Failed to load deals")
  } finally {
    loading.value = false
  }
}

const loadProperties = async () => {
  try {
    const response = await propertiesApi.getAll({ status: 'active', page_size: 100 })
    properties.value = response.data.properties || response.data
  } catch (err) {
    console.error('Failed to load properties:', err)
  }
}

const loadUsers = async () => {
  try {
    const response = await usersApi.getAll({ page_size: 100 })
    allUsers.value = response.data.users || response.data
  } catch (err) {
    console.error('Failed to load users:', err)
  }
}

const openCreateDialog = () => {
  resetForm()
  showCreateDialog.value = true
}

const viewDeal = (deal: Deal) => {
  selectedDeal.value = deal
  showDetailDialog.value = true
}

const updateStatus = (deal: Deal) => {
  selectedDeal.value = deal
  newStatus.value = ""
  statusNote.value = ""
  showStatusDialog.value = true
}

const confirmStatusUpdate = async () => {
  if (!selectedDeal.value || !newStatus.value) return
  try {
    await dealsApi.update(selectedDeal.value.id, {
      status: newStatus.value,
      note: statusNote.value || undefined
    })
    ElMessage.success("Status updated")
    showStatusDialog.value = false
    loadDeals()
  } catch (err: any) {
    const msg = err.response?.data?.detail || "Failed to update status"
    ElMessage.error(msg)
  }
}

const saveDeal = async () => {
  if (!form.value.property_id) {
    ElMessage.warning("Please select a property")
    return
  }
  if (!form.value.offer_price || form.value.offer_price <= 0) {
    ElMessage.warning("Please enter a valid offer price")
    return
  }

  try {
    // Build the request payload
    const payload: any = {
      property_id: form.value.property_id,
      offer_price: form.value.offer_price,
      participants: {},
      conditions: []
    }

    // Add optional fields
    if (form.value.closing_date) {
      payload.closing_date = form.value.closing_date
    }
    if (form.value.notes) {
      payload.notes = form.value.notes
    }

    // Add participants (only non-empty ones)
    const participantFields = ['buyer_id', 'seller_id', 'buyer_agent_id', 'seller_agent_id', 'buyer_lawyer_id', 'seller_lawyer_id']
    participantFields.forEach(field => {
      const value = form.value.participants[field as keyof typeof form.value.participants]
      if (value) {
        payload.participants[field] = value
      }
    })

    await dealsApi.create(payload)
    ElMessage.success("Deal created successfully")
    showCreateDialog.value = false
    resetForm()
    loadDeals()
  } catch (err: any) {
    const msg = err.response?.data?.detail || "Failed to create deal"
    ElMessage.error(msg)
  }
}

const deleteDeal = async (id: string) => {
  try {
    await ElMessageBox.confirm("Delete this deal? Only draft deals can be deleted.", "Warning", { type: "warning" })
    await dealsApi.delete(id)
    ElMessage.success("Deal deleted")
    loadDeals()
  } catch (error: any) {
    if (error !== "cancel") {
      const msg = error.response?.data?.detail || "Failed to delete deal"
      ElMessage.error(msg)
    }
  }
}

const resetForm = () => {
  form.value = {
    property_id: "",
    offer_price: 0,
    closing_date: null,
    notes: "",
    participants: {
      buyer_id: "",
      seller_id: "",
      buyer_agent_id: "",
      seller_agent_id: "",
      buyer_lawyer_id: "",
      seller_lawyer_id: ""
    },
    conditions: []
  }
}

onMounted(() => {
  loadDeals()
  loadProperties()
  loadUsers()
})
</script>

<style scoped>
.deals { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
h4 { margin-top: 20px; margin-bottom: 10px; }
</style>
