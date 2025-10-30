<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Notivue, NotivueSwipe, Notification, slateTheme } from 'notivue'
import FadeTransition from '@/components/shared/FadeTransition.vue'
</script>

<template>
  <Notivue v-slot="item">
    <NotivueSwipe :item="item">
      <Notification :item="item" :theme="slateTheme" />
    </NotivueSwipe>
  </Notivue>
  <RouterView v-slot="{ Component, route }">
    <FadeTransition>
      <component :is="Component" :key="route.fullPath" />
    </FadeTransition>
  </RouterView>
</template>
