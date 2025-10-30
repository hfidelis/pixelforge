import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth.store'

export function useAuth() {
  const auth = useAuthStore()
  const { user, token, loading } = storeToRefs(auth)

  return {
    user,
    token,
    loading,
    login: auth.login,
    logout: auth.logout,
    fetchUser: auth.fetchUser,
    isAuthenticated: computed(() => !!token.value),
  }
}
