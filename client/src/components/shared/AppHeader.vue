<script setup lang="ts">
import { push } from 'notivue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { ElHeader, ElButton, ElImage } from 'element-plus'

import LangSelect from './LangSelect.vue'

interface HeaderProps {
  username: string
}

const router = useRouter()
const props = defineProps<HeaderProps>()

const { logout } = useAuth()

const handleLogout = async () => {
  try {
    await logout()
    push.success({ title: 'Saindo', message: 'Você saiu com sucesso.' })
    router.push({ name: 'signin' })
  } catch {
    push.error({ title: 'Erro', message: 'Falha ao sair.' })
  }
}
</script>

<template>
  <ElHeader class="flex items-center justify-between px-4 md:px-8 py-4 bg-transparent">
    <div class="flex items-center gap-4">
      <ElImage src="/images/logo.webp" alt="logo" class="w-8 h-8 md:w-12 md:h-12" fit="contain" />
      <div class="hidden sm:block">
        <p
          class="bg-gradient-to-r from-cyan-600 to-green-400 bg-clip-text text-transparent text-md md:text-2xl font-semibold"
        >
          PixelForge
        </p>
      </div>
    </div>

    <div class="flex items-center flex-row-reverse md:flex-row gap-4">
      <div class="text-sm hidden md:block md:text-lg text-slate-200">
        {{ $t('components.shared.header.salutation') }}
        <span class="font-medium text-emerald-200 ms-1">
          {{ props.username }}
        </span>!
      </div>

      <ElButton color="#10B981" size="default" @click="handleLogout">
        {{ $t('components.shared.header.logout') }}
      </ElButton>
      <LangSelect />
    </div>
  </ElHeader>
</template>
