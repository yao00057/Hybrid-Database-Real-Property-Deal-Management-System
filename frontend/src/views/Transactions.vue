<template>
  <div class="transactions">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Financial Transactions</span>
          <el-button type="primary" @click="showCreateDialog = true">Create Transaction</el-button>
        </div>
      </template>

      <el-table :data="transactions" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="deal_id" label="Deal ID" width="220" />
        <el-table-column prop="transaction_type" label="Type">
          <template #default="{ row }">
            <el-tag>{{ row.transaction_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="Amount">
          <template #default="{ row }">
            ${{ row.amount?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="from_party" label="From" />
        <el-table-column prop="to_party" label="To" />
        <el-table-column prop="status" label="Status">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="completeTransaction(row.id)"
                       :disabled="row.status !== 'pending'">Complete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Trust Accounts</span>
              <el-button size="small" type="primary" @click="showTrustDialog = true">Add Account</el-button>
            </div>
          </template>
          <el-table :data="trustAccounts" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="account_name" label="Account Name" />
            <el-table-column prop="account_holder" label="Holder" />
            <el-table-column prop="balance" label="Balance">
              <template #default="{ row }">
                ${{ row.balance?.toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Recent Audit Logs</span>
          </template>
          <el-table :data="auditLogs" stripe size="small">
            <el-table-column prop="table_name" label="Table" width="100" />
            <el-table-column prop="action" label="Action" width="80" />
            <el-table-column prop="performed_by" label="By" />
            <el-table-column prop="performed_at" label="Time">
              <template #default="{ row }">
                {{ new Date(row.performed_at).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showCreateDialog" title="Create Transaction" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Deal ID">
          <el-input v-model="form.deal_id" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="form.transaction_type">
            <el-option label="Deposit" value="deposit" />
            <el-option label="Commission" value="commission" />
            <el-option label="Legal Fee" value="legal_fee" />
            <el-option label="Tax" value="tax" />
            <el-option label="Adjustment" value="adjustment" />
            <el-option label="Disbursement" value="disbursement" />
          </el-select>
        </el-form-item>
        <el-form-item label="Amount">
          <el-input-number v-model="form.amount" :min="0" :step="100" />
        </el-form-item>
        <el-form-item label="From Party">
          <el-input v-model="form.from_party" />
        </el-form-item>
        <el-form-item label="To Party">
          <el-input v-model="form.to_party" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveTransaction">Create</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTrustDialog" title="Create Trust Account" width="400px">
      <el-form :model="trustForm" label-width="120px">
        <el-form-item label="Account Name">
          <el-input v-model="trustForm.account_name" />
        </el-form-item>
        <el-form-item label="Holder">
          <el-input v-model="trustForm.account_holder" />
        </el-form-item>
        <el-form-item label="Initial Balance">
          <el-input-number v-model="trustForm.initial_balance" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTrustDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveTrustAccount">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { transactionsApi } from "../api"
import type { Transaction, TransactionCreate, TrustAccount, AuditLog } from "../types"

const transactions = ref<Transaction[]>([])
const trustAccounts = ref<TrustAccount[]>([])
const auditLogs = ref<AuditLog[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showTrustDialog = ref(false)

const form = ref<TransactionCreate>({
  deal_id: "",
  transaction_type: "deposit",
  amount: 0,
  from_party: "",
  to_party: "",
  description: ""
})

const trustForm = ref({
  account_name: "",
  account_holder: "",
  initial_balance: 0
})

const loadData = async () => {
  loading.value = true
  try {
    const [txRes, trustRes, logsRes] = await Promise.all([
      transactionsApi.getAll(),
      transactionsApi.getTrustAccounts(),
      transactionsApi.getAuditLogs({ limit: 10 })
    ])
    transactions.value = txRes.data
    trustAccounts.value = trustRes.data
    auditLogs.value = logsRes.data
  } catch {
    ElMessage.error("Failed to load data")
  } finally {
    loading.value = false
  }
}

const saveTransaction = async () => {
  try {
    await transactionsApi.create(form.value)
    ElMessage.success("Transaction created")
    showCreateDialog.value = false
    resetForm()
    loadData()
  } catch {
    ElMessage.error("Failed to create transaction")
  }
}

const completeTransaction = async (id: number) => {
  try {
    await transactionsApi.complete(id)
    ElMessage.success("Transaction completed")
    loadData()
  } catch {
    ElMessage.error("Failed to complete transaction")
  }
}

const saveTrustAccount = async () => {
  try {
    await transactionsApi.createTrustAccount(trustForm.value)
    ElMessage.success("Trust account created")
    showTrustDialog.value = false
    trustForm.value = { account_name: "", account_holder: "", initial_balance: 0 }
    loadData()
  } catch {
    ElMessage.error("Failed to create trust account")
  }
}

const resetForm = () => {
  form.value = {
    deal_id: "",
    transaction_type: "deposit",
    amount: 0,
    from_party: "",
    to_party: "",
    description: ""
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.transactions { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
