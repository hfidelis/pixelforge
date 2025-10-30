import { defineStore } from 'pinia'
import type { User, AuthState } from '@/types/auth'
import authService from '@/api/services/auth.service'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    loading: false,
  }),
  actions: {
    async login(email: string, password: string) {
      this.loading = true
      return new Promise<void>(async (resolve, reject) => {
        try {
          const { access_token } = await authService.login({ email, password })
          this.token = access_token
          localStorage.setItem('token', access_token)
          await this.fetchUser()
          resolve()
        } catch (err) {
          this.logout()
          reject(err)
        } finally {
          this.loading = false
        }
      })
    },
    async fetchUser() {
      if (!this.token) return

      return new Promise<void>(async (resolve, reject) => {
        try {
          const user: User = await authService.getCurrentUser()
          this.user = user
          resolve()
        } catch (err) {
          this.logout()
          reject(err)
        }
      })
    },
    async logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
    async initialize() {
      if (this.token && !this.user) {
        this.loading = true
        try {
          await this.fetchUser()
        } catch {
          this.logout()
        } finally {
          this.loading = false
        }
      }
    },
  },
  persist: true,
})
