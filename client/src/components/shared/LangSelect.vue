<script lang="ts" setup>
import i18n from '@/i18n'
import { ref } from 'vue'

import ptBR from '/images/pt-BR.webp'
import enUS from '/images/en-US.webp'

const langs = [
  { value: 'pt-BR', label: 'Português (BR)', img: ptBR },
  { value: 'en-US', label: 'English (US)', img: enUS },
]

const avaliableLangs = i18n.global.availableLocales.map((lang) => {
  return langs.find((l) => l.value === lang)
})

const value = ref(i18n.global.locale)
</script>

<template>
  <el-select v-model="value" placeholder="Select" style="width: 240px" dark>
    <el-option
      v-for="item in avaliableLangs"
      :key="item!.value"
      :label="item!.label"
      :value="item!.value"
    >
      <div class="flex items-center">
        <img
          :src="item!.img"
          :alt="item!.label"
          style="width: 24px; height: 16px; margin-right: 8px; vertical-align: middle"
        />
        <span style="float: left" class="hidden md:inline-block">{{ item!.label }}</span>
      </div>
    </el-option>
    <template #label="{ value }">
      <div class="flex items-center">
        <img
          :src="langs.find((l) => l.value === value)!.img"
          :alt="langs.find((l) => l.value === value)!.label"
          style="width: 24px; height: 16px; margin-right: 8px; vertical-align: middle"
        />
        <span style="vertical-align: middle" class="hidden md:inline-block">
          {{ langs.find((l) => l.value === value)!.label }}
        </span>
      </div>
    </template>
  </el-select>
</template>

<style lang="scss">
.el-select {
  width: 180px !important;
}

@media (max-width: 768px) {
  .el-select {
    width: 90px !important;
  }
}
</style>
