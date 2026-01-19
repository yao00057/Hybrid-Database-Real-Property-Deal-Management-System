<template>
  <div class="transactions-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Transactions</span>
              <el-button type="primary" @click="openAddDialog">
                <el-icon><Plus /></el-icon>
                Record Transaction
              </el-button>
            </div>
          </template>

          <el-row :gutter="20" class="filter-row">
            <el-col :span="8">
              <el-input v-model="filterDealId" placeholder="Filter by Deal ID" clearable @change="loadTransactions" />
            </el-col>
            <el-col :span="6">
              <el-select v-model="filterType" placeholder="Type" clearable @change="loadTransactions">
                <el-option label="Deposit" value="deposit" />
                <el-option label="Payment" value="payment" />
                <el-option label="Refund" value="refund" />
                <el-option label="Commission" value="commission" />
              </el-select>
            </el-col>
          </el-row>

          <el-table :data="transactions" stripe v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="deal_id" label="Deal ID" width="120">
              <template #default="{ row }">
                {{ row.deal_id.substring(0, 8) }}...
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="Amount" width="130">
              <template #default="{ row }">
                <span :class="row.transaction_type === 'refund' ? 'text-danger' : 'text-success'">
                  ${{ row.amount.toLocaleString() }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="transaction_type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="getTypeTagType(row.transaction_type)" size="small">
                  {{ row.transaction_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="Date" width="160">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next, total"
            @current-change="loadTransactions"
            class="pagination"
          />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Trust Accounts</span>
              <el-button size="small" type="primary" @click="openAccountDialog">
                <el-icon><Plus /></el-icon>
                Add
              </el-button>
            </div>
          </template>

          <el-table :data="accounts" size="small" v-loading="accountsLoading">
            <el-table-column prop="account_number" label="Account #" width="100" />
            <el-table-column prop="holder_name" label="Holder" min-width="100" />
            <el-table-column prop="balance" label="Balance" width="110">
              <template #default="{ row }">
                ${{ row.balance.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add Transaction Dialog -->
    <el-dialog v-model="addDialogVisible" title="Record Transaction" width="500">
      <el-form :model="transactionForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Deal ID" prop="deal_id">
          <el-input v-model="transactionForm.deal_id" placeholder="MongoDB ObjectId" />
        </el-form-item>
        <el-form-item label="Amount" prop="amount">
          <el-input-number v-model="transactionForm.amount" :min="0.01" :step="100" :precision="2" style="width: 200px" />
        </el-form-item>
        <el-form-item label="Type" prop="transaction_type">
          <el-select v-model="transactionForm.transaction_type" style="width: 100%">
            <el-option label="Deposit" value="deposit" />
            <el-option label="Payment" value="payment" />
            <el-option label="Refund" value="refund" />
            <el-option label="Commission" value="commission" />
            <el-option label="Adjustment" value="adjustment" />
          </el-select>
        </el-form-item>
        <el-form-item label="From Account">
          <el-select v-model="transactionForm.from_account" placeholder="Select account" clearable style="width: 100%">
            <el-option v-for="acc in accounts" :key="acc.id" :label="`${acc.account_number} - ${acc.holder_name}`" :value="acc.account_number" />
          </el-select>
        </el-form-item>
        <el-form-item label="To Account">
          <el-select v-model="transactionForm.to_account" placeholder="Select account" clearable style="width: 100%">
            <el-option v-for="acc in accounts" :key="acc.id" :label="`${acc.account_number} - ${acc.holder_name}`" :value="acc.account_number" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="transactionForm.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createTransaction" :loading="saving">Save</el-button>
      </template>
    </el-dialog>

    <!-- Add Account Dialog -->
    <el-dialog v-model="accountDialogVisible" title="Create Trust Account" width="400">
      <el-form :model="accountForm" :rules="accountRules" ref="accountFormRef" label-width="110px">
        <el-form-item label="Account #" prop="account_number">
          <el-input v-model="accountForm.account_number" />
        </el-form-item>
        <el-form-item label="Holder Name" prop="holder_name">
          <el-input v-model="accountForm.holder_name" />
        </el-form-item>
        <el-form-item label="Initial Balance">
          <el-input-number v-model="accountForm.initial_balance" :min="0" :step="1000" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="accountDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createAccount" :loading="saving">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { transactionApi, trustAccountApi } from '../api/index'
import type { Transaction, TrustAccount } from '../types'

const transactions = ref<Transaction[]>([])
const accounts = ref<TrustAccount[]>([])
const loading = ref(false)
const accountsLoading = ref(false)
const saving = ref(false)
const addDialogVisible = ref(false)
const accountDialogVisible = ref(false)
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)
const filterDealId = ref('')
const filterType = ref('')
const formRef = ref<FormInstance>()
const accountFormRef = ref<FormInstance>()

const transactionForm = reactive({
  deal_id: '',
  amount: 0,
  transaction_type: 'deposit',
  from_account: '',
  to_account: '',
  description: ''
})

const accountForm = reactive({
  account_number: '',
  holder_name: '',
  initial_balance: 0
})

const rules: FormRules = {
  deal_id: [{ required: true, message: 'Deal ID is required', trigger: 'blur' }],
  amount: [{ required: true, type: 'number', min: 0.01, message: 'Valid amount required', trigger: 'blur' }],
  transaction_type: [{ required: true, message: 'Type is required', trigger: 'change' }]
}

const accountRules: FormRules = {
  account_number: [{ required: true, min: 5, message: 'Min 5 characters', trigger: 'blur' }],
  holder_name: [{ required: true, message: 'Holder name is required', trigger: 'blur' }]
}

const loadTransactions = async () => {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize }
    if (filterDealId.value) params.deal_id = filterDealId.value
    if (filterType.value) params.type = filterType.value
    const response = await transactionApi.getAll(params)
    transactions.value = response.transactions
    total.value = response.total
  } catch (error) {
    console.error('Failed to load transactions:', error)
  } finally {
    loading.value = false
  }
}

const loadAccounts = async () => {
  accountsLoading.value = true
  try {
    const response = await trustAccountApi.getAll()
    accounts.value = response.accounts
  } catch (error) {
    console.error('Failed to load accounts:', error)
  } finally {
    accountsLoading.value = false
  }
}

const openAddDialog = () => {
  transactionForm.deal_id = ''
  transactionForm.amount = 0
  transactionForm.transaction_type = 'deposit'
  transactionForm.from_account = ''
  transactionForm.to_account = ''
  transactionForm.description = ''
  addDialogVisible.value = true
}

const openAccountDialog = () => {
  accountForm.account_number = ''
  accountForm.holder_name = ''
  accountForm.initial_balance = 0
  accountDialogVisible.value = true
}

const createTransaction = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      await transactionApi.create({
        deal_id: transactionForm.deal_id,
        amount: transactionForm.amount,
        transaction_type: transactionForm.transaction_type as any,
        from_account: transactionForm.from_account || undefined,
        to_account: transactionForm.to_account || undefined,
        description: transactionForm.description || undefined
      })
      ElMessage.success('Transaction recorded successfully')
      addDialogVisible.value = false
      loadTransactions()
    } catch (error) {
      console.error('Failed to create transaction:', error)
    } finally {
      saving.value = false
    }
  })
}

const createAccount = async () => {
  if (!accountFormRef.value) return
  await accountFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      await trustAccountApi.create({
        account_number: accountForm.account_number,
        holder_name: accountForm.holder_name,
        initial_balance: accountForm.initial_balance
      })
      ElMessage.success('Account created successfully')
      accountDialogVisible.value = false
      loadAccounts()
    } catch (error) {
      console.error('Failed to create account:', error)
    } finally {
      saving.value = false
    }
  })
}

const getTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    deposit: 'success',
    payment: 'primary',
    refund: 'danger',
    commission: 'warning',
    adjustment: 'info'
  }
  return types[type] || 'default'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    completed: 'success',
    failed: 'danger',
    reversed: 'info'
  }
  return types[status] || 'default'
}

onMounted(() => {
  loadTransactions()
  loadAccounts()
})
</script>

<style scoped>
.transactions-container {
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

.text-success {
  color: #67c23a;
  font-weight: bold;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
