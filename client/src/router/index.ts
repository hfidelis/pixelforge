import SignIn from '@/views/SignIn.vue'
import HomeView from '@/views/HomeView.vue'

import { useAuthStore } from '@/stores/auth.store'
import { createRouter, createWebHistory } from 'vue-router'
import SignUp from '@/views/SignUp.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/signin',
      name: 'signin',
      component: SignIn,
      meta: {
        guestOnly: true,
        requiresAuth: false,
      },
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp,
      meta: {
        guestOnly: true,
        requiresAuth: false,
      },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  const isAuthenticated = !!authStore.user

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'signin' })
  } else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
