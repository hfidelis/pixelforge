import axiosService from '@/api/core/axios.service'
import type { AxiosInstance } from 'axios'
import type { LoginCredentials, AuthResponse, RegisterCredentials } from '@/types/auth'

class AuthService {
  private static instance: AuthService
  private axios: AxiosInstance
  private service: typeof axiosService

  private constructor() {
    this.axios = axiosService.getAxios()
    this.service = axiosService
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService()
    }
    return AuthService.instance
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data } = await this.axios.post<AuthResponse>('auth/signin', credentials)
    this.service.setToken(data.access_token)
    return data
  }

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const { data } = await this.axios.post<AuthResponse>('auth/register', credentials)

    return data
  }

  async getCurrentUser() {
    const { data } = await this.axios.get('user/me')
    return data
  }

  logout() {
    axiosService.clearToken()
  }
}

const authService = AuthService.getInstance()

export default authService
