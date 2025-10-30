import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

class AxiosService {
  private static instance: AxiosService
  private axiosInstance: AxiosInstance
  private token: string | null = null

  private constructor() {
    this.token = localStorage.getItem('token')

    this.axiosInstance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/',
      timeout: 60000,
    })

    this.initializeInterceptors()
  }

  public static getInstance(): AxiosService {
    if (!AxiosService.instance) {
      AxiosService.instance = new AxiosService()
    }
    return AxiosService.instance
  }

  private initializeInterceptors() {
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => Promise.reject(error),
    )

    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.handleUnauthorized()
        }
        return Promise.reject(error)
      },
    )
  }

  private handleUnauthorized() {
    this.clearToken()

    window.dispatchEvent(new CustomEvent('unauthorized'))
  }

  public setToken(token: string) {
    this.token = token
    localStorage.setItem('token', token)
  }

  public clearToken() {
    this.token = null
    localStorage.removeItem('token')
  }

  public getAxios(): AxiosInstance {
    return this.axiosInstance
  }
}

const axiosService = AxiosService.getInstance()

export default axiosService
