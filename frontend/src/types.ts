// User types
export type UserRole = 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent' | 'buyer_lawyer' | 'seller_lawyer'

export interface Profile {
  name: string
  phone?: string
  address?: string
}

export interface User {
  _id: string
  email: string
  role: UserRole
  profile: Profile
  role_specific?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface UserCreate {
  email: string
  password: string
  role: UserRole
  profile: Profile
  role_specific?: Record<string, any>
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  page_size: number
}

// Property types
export type PropertyType = 'residential' | 'commercial'
export type PropertyStatus = 'active' | 'pending' | 'sold' | 'withdrawn'

export interface Address {
  street: string
  city: string
  province: string
  postal_code: string
  country: string
}

export interface Property {
  _id: string
  type: PropertyType
  address: Address
  listing_price: number
  status: PropertyStatus
  attributes: Record<string, any>
  description?: string
  images: string[]
  created_at: string
  updated_at: string
}

export interface PropertyCreate {
  type: PropertyType
  address: Address
  listing_price: number
  attributes?: Record<string, any>
  description?: string
}

export interface PropertyUpdate {
  listing_price?: number
  status?: PropertyStatus
  attributes?: Record<string, any>
  description?: string
}

export interface PropertyListResponse {
  properties: Property[]
  total: number
  page: number
  page_size: number
}

// Deal types
export type DealStatus = 'draft' | 'submitted' | 'conditional' | 'firm' | 'closing' | 'completed' | 'cancelled' | 'expired'
export type ConditionType = 'financing' | 'inspection' | 'appraisal' | 'sale_of_property' | 'other'
export type ConditionStatus = 'pending' | 'satisfied' | 'waived' | 'failed'

export interface Condition {
  id: string
  type: ConditionType
  description?: string
  deadline?: string
  status: ConditionStatus
  satisfied_at?: string
}

export interface ParticipantSnapshot {
  user_id: string
  name: string
  email: string
  phone?: string
  role_type: string
  license_number?: string
  brokerage?: string
  law_firm?: string
}

export interface Deal {
  _id: string
  property_id: string
  offer_price: number
  status: DealStatus
  participants_snapshot: Record<string, ParticipantSnapshot>
  participant_refs: Record<string, string>
  conditions: Condition[]
  closing_date?: string
  notes?: string
  status_history: Array<{ status: string; timestamp: string; note?: string }>
  snapshot_timestamp: string
  created_at: string
  updated_at: string
}

export interface DealCreate {
  property_id: string
  offer_price: number
  participants: {
    buyer_id?: string
    seller_id?: string
    buyer_agent_id?: string
    seller_agent_id?: string
    buyer_lawyer_id?: string
    seller_lawyer_id?: string
  }
  closing_date?: string
  conditions?: Array<{ type: ConditionType; description?: string; deadline?: string }>
  notes?: string
}

export interface DealListResponse {
  deals: Deal[]
  total: number
  page: number
  page_size: number
}

// Transaction types
export type TransactionType = 'deposit' | 'payment' | 'refund' | 'commission' | 'adjustment'
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'reversed'
export type AccountStatus = 'active' | 'frozen' | 'closed'

export interface Transaction {
  id: number
  deal_id: string
  amount: number
  transaction_type: TransactionType
  status: TransactionStatus
  from_account?: string
  to_account?: string
  description?: string
  created_at: string
}

export interface TransactionCreate {
  deal_id: string
  amount: number
  transaction_type: TransactionType
  from_account?: string
  to_account?: string
  description?: string
}

export interface TransactionListResponse {
  transactions: Transaction[]
  total: number
  page: number
  page_size: number
}

export interface TrustAccount {
  id: number
  account_number: string
  holder_name: string
  balance: number
  status: AccountStatus
  created_at: string
  updated_at: string
}

export interface TrustAccountCreate {
  account_number: string
  holder_name: string
  initial_balance?: number
}
