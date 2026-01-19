<template>
  <div class="deals">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Deal Management</span>
          <el-button type="primary" @click="showCreateDialog = true">Create Deal</el-button>
        </div>
      </template>

      <el-row :gutter="10" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="Status" clearable @change="loadDeals">
            <el-option label="Draft" value="draft" />
            <el-option label="Submitted" value="submitted" />
            <el-option label="Under Review" value="under_review" />
            <el-option label="Accepted" value="accepted" />
            <el-option label="Conditional" value="conditional" />
            <el-option label="Firm" value="firm" />
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
        <el-table-column prop="deposit_amount" label="Deposit">
          <template #default="{ row }">
            ${{ row.deposit_amount?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="Participants">
          <template #default="{ row }">
            {{ row.participants?.length || 0 }} participants
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

    <el-dialog v-model="showCreateDialog" title="Create Deal" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Property ID">
          <el-input v-model="form.property_id" />
        </el-form-item>
        <el-form-item label="Buyer ID">
          <el-input v-model="form.buyer_id" />
        </el-form-item>
        <el-form-item label="Seller ID">
          <el-input v-model="form.seller_id" />
        </el-form-item>
        <el-form-item label="Offer Price">
          <el-input-number v-model="form.offer_price" :min="0" :step="10000" />
        </el-form-item>
        <el-form-item label="Deposit">
          <el-input-number v-model="form.deposit_amount" :min="0" :step="1000" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="form.notes" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveDeal">Create</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="Deal Details" width="700px">
      <div v-if="selectedDeal">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedDeal.status)">{{ selectedDeal.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Offer">${{ selectedDeal.offer_price?.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Deposit">${{ selectedDeal.deposit_amount?.toLocaleString() }}</el-descriptions-item>
        </el-descriptions>
        <h4>Participants</h4>
        <el-table :data="selectedDeal.participants" stripe size="small">
          <el-table-column prop="name" label="Name" />
          <el-table-column prop="role" label="Role" />
          <el-table-column prop="email" label="Email" />
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="showStatusDialog" title="Update Status" width="400px">
      <el-select v-model="newStatus" placeholder="Select new status" style="width: 100%">
        <el-option label="Submitted" value="submitted" />
        <el-option label="Under Review" value="under_review" />
        <el-option label="Accepted" value="accepted" />
        <el-option label="Conditional" value="conditional" />
        <el-option label="Firm" value="firm" />
        <el-option label="Completed" value="completed" />
        <el-option label="Cancelled" value="cancelled" />
      </el-select>
      <template #footer>
        <el-button @click="showStatusDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmStatusUpdate">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { dealsApi } from "../api"
import type { Deal, DealCreate } from "../types"

const deals = ref<Deal[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showStatusDialog = ref(false)
const selectedDeal = ref<Deal | null>(null)
const newStatus = ref("")
const filters = ref({ status: "" })

const form = ref<DealCreate>({
  property_id: "",
  buyer_id: "",
  seller_id: "",
  offer_price: 0,
  deposit_amount: 0,
  notes: ""
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: "info", submitted: "warning", under_review: "warning",
    accepted: "primary", conditional: "warning", firm: "success",
    completed: "success", cancelled: "danger"
  }
  return types[status] || "info"
}

const loadDeals = async () => {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.value.status) params.status = filters.value.status
    const response = await dealsApi.getAll(params)
    deals.value = response.data
  } catch {
    ElMessage.error("Failed to load deals")
  } finally {
    loading.value = false
  }
}

const viewDeal = (deal: Deal) => {
  selectedDeal.value = deal
  showDetailDialog.value = true
}

const updateStatus = (deal: Deal) => {
  selectedDeal.value = deal
  newStatus.value = ""
  showStatusDialog.value = true
}

const confirmStatusUpdate = async () => {
  if (!selectedDeal.value || !newStatus.value) return
  try {
    await dealsApi.update(selectedDeal.value.id, { status: newStatus.value })
    ElMessage.success("Status updated")
    showStatusDialog.value = false
    loadDeals()
  } catch {
    ElMessage.error("Failed to update status")
  }
}

const saveDeal = async () => {
  try {
    await dealsApi.create(form.value)
    ElMessage.success("Deal created")
    showCreateDialog.value = false
    resetForm()
    loadDeals()
  } catch {
    ElMessage.error("Failed to create deal")
  }
}

const deleteDeal = async (id: string) => {
  try {
    await ElMessageBox.confirm("Delete this deal?", "Warning", { type: "warning" })
    await dealsApi.delete(id)
    ElMessage.success("Deal deleted")
    loadDeals()
  } catch (error) {
    if (error !== "cancel") ElMessage.error("Failed to delete deal")
  }
}

const resetForm = () => {
  form.value = { property_id: "", buyer_id: "", seller_id: "", offer_price: 0, deposit_amount: 0, notes: "" }
}

onMounted(() => loadDeals())
</script>

<style scoped>
.deals { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
h4 { margin-top: 20px; }
</style>
