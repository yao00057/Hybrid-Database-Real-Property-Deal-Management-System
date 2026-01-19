<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>User Management</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            Add User
          </el-button>
        </div>
      </template>

      <el-row :gutter="20" class="filter-row">
        <el-col :span="6">
          <el-select v-model="filterRole" placeholder="Filter by role" clearable @change="loadUsers">
            <el-option label="Buyer" value="buyer" />
            <el-option label="Seller" value="seller" />
            <el-option label="Buyer Agent" value="buyer_agent" />
            <el-option label="Seller Agent" value="seller_agent" />
            <el-option label="Buyer Lawyer" value="buyer_lawyer" />
            <el-option label="Seller Lawyer" value="seller_lawyer" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="users" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="profile.name" label="Name" min-width="150" />
        <el-table-column prop="email" label="Email" min-width="200" />
        <el-table-column prop="role" label="Role" width="130">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">{{ formatRole(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="profile.phone" label="Phone" width="130" />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">Edit</el-button>
            <el-button size="small" type="danger" @click="confirmDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="loadUsers"
        class="pagination"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit User' : 'Add User'" width="500">
      <el-form :model="userForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Email" prop="email">
          <el-input v-model="userForm.email" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="Password" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="userForm.role" :disabled="isEdit" style="width: 100%">
            <el-option label="Buyer" value="buyer" />
            <el-option label="Seller" value="seller" />
            <el-option label="Buyer Agent" value="buyer_agent" />
            <el-option label="Seller Agent" value="seller_agent" />
            <el-option label="Buyer Lawyer" value="buyer_lawyer" />
            <el-option label="Seller Lawyer" value="seller_lawyer" />
          </el-select>
        </el-form-item>
        <el-form-item label="Name" prop="profile.name">
          <el-input v-model="userForm.profile.name" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="userForm.profile.phone" />
        </el-form-item>
        <el-form-item label="Address">
          <el-input v-model="userForm.profile.address" />
        </el-form-item>

        <!-- Role-specific fields for agents -->
        <template v-if="userForm.role?.includes('agent')">
          <el-divider>Agent Information</el-divider>
          <el-form-item label="License #">
            <el-input v-model="userForm.role_specific.license_number" />
          </el-form-item>
          <el-form-item label="Brokerage">
            <el-input v-model="userForm.role_specific.brokerage" />
          </el-form-item>
        </template>

        <!-- Role-specific fields for lawyers -->
        <template v-if="userForm.role?.includes('lawyer')">
          <el-divider>Lawyer Information</el-divider>
          <el-form-item label="Bar #">
            <el-input v-model="userForm.role_specific.bar_number" />
          </el-form-item>
          <el-form-item label="Law Firm">
            <el-input v-model="userForm.role_specific.law_firm" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { userApi } from '../api/index'
import type { User } from '../types'

const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)
const filterRole = ref('')
const formRef = ref<FormInstance>()

const userForm = reactive({
  email: '',
  password: '',
  role: '' as string,
  profile: {
    name: '',
    phone: '',
    address: ''
  },
  role_specific: {} as Record<string, any>
})

const rules: FormRules = {
  email: [{ required: true, type: 'email', message: 'Valid email required', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: 'Min 6 characters', trigger: 'blur' }],
  role: [{ required: true, message: 'Role is required', trigger: 'change' }],
  'profile.name': [{ required: true, message: 'Name is required', trigger: 'blur' }]
}

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await userApi.getAll(currentPage.value, pageSize, filterRole.value || undefined)
    users.value = response.users
    total.value = response.total
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editUser = (user: User) => {
  isEdit.value = true
  editingId.value = user._id
  userForm.email = user.email
  userForm.role = user.role
  userForm.profile.name = user.profile.name
  userForm.profile.phone = user.profile.phone || ''
  userForm.profile.address = user.profile.address || ''
  userForm.role_specific = user.role_specific || {}
  dialogVisible.value = true
}

const resetForm = () => {
  userForm.email = ''
  userForm.password = ''
  userForm.role = ''
  userForm.profile.name = ''
  userForm.profile.phone = ''
  userForm.profile.address = ''
  userForm.role_specific = {}
}

const saveUser = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      if (isEdit.value) {
        await userApi.update(editingId.value, {
          profile: userForm.profile,
          role_specific: userForm.role_specific
        })
        ElMessage.success('User updated successfully')
      } else {
        await userApi.create({
          email: userForm.email,
          password: userForm.password,
          role: userForm.role as any,
          profile: userForm.profile,
          role_specific: userForm.role_specific
        })
        ElMessage.success('User created successfully')
      }
      dialogVisible.value = false
      loadUsers()
    } catch (error) {
      console.error('Failed to save user:', error)
    } finally {
      saving.value = false
    }
  })
}

const confirmDelete = (user: User) => {
  ElMessageBox.confirm(
    `Are you sure you want to delete ${user.profile.name}?`,
    'Confirm Delete',
    { type: 'warning' }
  ).then(async () => {
    try {
      await userApi.delete(user._id)
      ElMessage.success('User deleted')
      loadUsers()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }).catch(() => {})
}

const getRoleTagType = (role: string) => {
  const types: Record<string, string> = {
    buyer: 'primary',
    seller: 'success',
    buyer_agent: 'warning',
    seller_agent: 'warning',
    buyer_lawyer: 'info',
    seller_lawyer: 'info'
  }
  return types[role] || 'default'
}

const formatRole = (role: string) => {
  return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
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
