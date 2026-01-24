import axios from 'axios'

const api = axios.create({
  baseURL: 'http://192.168.232.139:8001/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: any) =>
    api.post('/auth/register', data),

  me: () =>
    api.get('/auth/me'),

  refresh: () =>
    api.post('/auth/refresh')
}

// Users API
export const usersApi = {
  getAll: (params?: any) => api.get('/users', { params }),
  getById: (id: string) => api.get(`/users/${id}`),
  create: (data: any) => api.post('/users', data),
  update: (id: string, data: any) => api.put(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`)
}

// Properties API
export const propertiesApi = {
  getAll: (params?: any) => api.get('/properties', { params }),
  getById: (id: string) => api.get(`/properties/${id}`),
  create: (data: any) => api.post('/properties', data),
  update: (id: string, data: any) => api.put(`/properties/${id}`, data),
  delete: (id: string) => api.delete(`/properties/${id}`)
}

// Deals API
export const dealsApi = {
  getAll: (params?: any) => api.get('/deals', { params }),
  getById: (id: string) => api.get(`/deals/${id}`),
  create: (data: any) => api.post('/deals', data),
  update: (id: string, data: any) => api.put(`/deals/${id}`, data),
  delete: (id: string) => api.delete(`/deals/${id}`)
}

// Transactions API
export const transactionsApi = {
  getAll: (params?: any) => api.get('/transactions', { params }),
  getById: (id: number) => api.get(`/transactions/${id}`),
  create: (data: any) => api.post('/transactions', data),
  complete: (id: number) => api.post(`/transactions/${id}/complete`),
  getTrustAccounts: () => api.get('/transactions/trust-accounts/list'),
  createTrustAccount: (data: any) => api.post('/transactions/trust-accounts', data),
  getAuditLogs: (params?: any) => api.get('/transactions/audit-logs/list', { params })
}

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getPropertyStats: () => api.get('/dashboard/properties'),
  getDealStats: () => api.get('/dashboard/deals'),
  getTransactionStats: () => api.get('/dashboard/transactions')
}

export default api
