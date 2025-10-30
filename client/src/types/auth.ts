export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
  username: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  email: string
  username?: string
  created_at: string
}

export interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
}
