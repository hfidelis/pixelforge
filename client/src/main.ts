import '@/assets/main.css'
import 'notivue/notification.css'
import 'notivue/animations.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createNotivue } from 'notivue'
import { useAuthStore } from '@/stores/auth.store'

import App from '@/App.vue'
import i18n from '@/i18n'
import router from '@/router'
import ElementPlus from 'element-plus'
import VueEasyLightbox from 'vue-easy-lightbox'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const notivue = createNotivue({
  limit: 5,
  avoidDuplicates: true,
  notifications: {
    global: {
      duration: 10000,
    },
  },
})

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)

app.use(i18n)
app.use(pinia)
app.use(router)
app.use(notivue)
app.use(ElementPlus)
app.use(VueEasyLightbox)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const authStore = useAuthStore()
await authStore.initialize()

window.addEventListener('unauthorized', () => {
  if (router.currentRoute.value.name !== 'signin') {
    authStore.logout()
    router.push({ name: 'signin' })
  }
})

app.mount('#app')
