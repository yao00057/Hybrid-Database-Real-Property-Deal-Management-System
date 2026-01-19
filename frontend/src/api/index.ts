import axios from 'axios'
import { ElMessage } from 'element-plus'
import type {
  User, UserCreate, UserListResponse,
  Property, PropertyCreate, PropertyUpdate, PropertyListResponse,
  Deal, DealCreate, DealListResponse,
  Transaction, TransactionCreate, TransactionListResponse,
  TrustAccount, TrustAccountCreate
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || 'An error occurred'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// User API
export const userApi = {
  getAll: (page = 1, pageSize = 10, role?: string): Promise<UserListResponse> =>
    api.get('/users', { params: { page, page_size: pageSize, role } }),

  getById: (id: string): Promise<User> =>
    api.get(`/users/${id}`),

  create: (data: UserCreate): Promise<User> =>
    api.post('/users', data),

  update: (id: string, data: Partial<UserCreate>): Promise<User> =>
    api.put(`/users/${id}`, data),

  delete: (id: string): Promise<void> =>
    api.delete(`/users/${id}`),

  getByRole: (role: string): Promise<User[]> =>
    api.get(`/users/role/${role}`)
}

// Property API
export const propertyApi = {
  getAll: (params: {
    page?: number
    page_size?: number
    type?: string
    status?: string
    min_price?: number
    max_price?: number
    city?: string
  } = {}): Promise<PropertyListResponse> =>
    api.get('/properties', { params }),

  getActive: (): Promise<Property[]> =>
    api.get('/properties/active'),

  getById: (id: string): Promise<Property> =>
    api.get(`/properties/${id}`),

  create: (data: PropertyCreate): Promise<Property> =>
    api.post('/properties', data),

  update: (id: string, data: PropertyUpdate): Promise<Property> =>
    api.put(`/properties/${id}`, data),

  delete: (id: string): Promise<void> =>
    api.delete(`/properties/${id}`)
}

// Deal API
export const dealApi = {
  getAll: (params: {
    page?: number
    page_size?: number
    status?: string
    property_id?: string
  } = {}): Promise<DealListResponse> =>
    api.get('/deals', { params }),

  getById: (id: string): Promise<Deal> =>
    api.get(`/deals/${id}`),

  create: (data: DealCreate): Promise<Deal> =>
    api.post('/deals', data),

  update: (id: string, data: { offer_price?: number; closing_date?: string; notes?: string }): Promise<Deal> =>
    api.put(`/deals/${id}`, data),

  updateStatus: (id: string, status: string, note?: string): Promise<Deal> =>
    api.patch(`/deals/${id}/status`, { status, note }),

  addCondition: (id: string, condition: { type: string; description?: string; deadline?: string }): Promise<Deal> =>
    api.post(`/deals/${id}/conditions`, condition),

  updateCondition: (dealId: string, conditionId: string, update: { status: string; description?: string }): Promise<Deal> =>
    api.patch(`/deals/${dealId}/conditions/${conditionId}`, update),

  delete: (id: string): Promise<void> =>
    api.delete(`/deals/${id}`)
}

// Transaction API
export const transactionApi = {
  getAll: (params: {
    page?: number
    page_size?: number
    deal_id?: string
    type?: string
  } = {}): Promise<TransactionListResponse> =>
    api.get('/transactions', { params }),

  getById: (id: number): Promise<Transaction> =>
    api.get(`/transactions/${id}`),

  getByDeal: (dealId: string): Promise<Transaction[]> =>
    api.get(`/deals/${dealId}/transactions`),

  create: (data: TransactionCreate): Promise<Transaction> =>
    api.post('/transactions', data)
}

// Trust Account API
export const trustAccountApi = {
  getAll: (): Promise<{ accounts: TrustAccount[]; total: number }> =>
    api.get('/accounts'),

  getById: (id: number): Promise<TrustAccount> =>
    api.get(`/accounts/${id}`),

  create: (data: TrustAccountCreate): Promise<TrustAccount> =>
    api.post('/accounts', data),

  update: (id: number, data: { holder_name?: string; status?: string }): Promise<TrustAccount> =>
    api.put(`/accounts/${id}`, data)
}

export default api
