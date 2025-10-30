<script setup lang="ts">
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

import jobService from '@/api/services/job.service'
import AppHeader from '@/components/shared/AppHeader.vue'
import JobUploadForm from '@/components/jobs/JobUploadForm.vue'

import { Upload, Document } from '@element-plus/icons-vue'
import JobTable from '@/components/jobs/JobTable.vue'

const { t } = useI18n()
const { user } = useAuth()

const fetchingFormats = ref(false)
const formats = ref<string[]>([])

const initFormats = async () => {
  fetchingFormats.value = true
  try {
    const response = await jobService.getJobImageFormats()
    formats.value = response || []
  } catch {
    push.error({
      title: t('views.home.error.formatFetch.title'),
      message: t('views.home.error.formatFetch.message'),
    })
  } finally {
    fetchingFormats.value = false
  }
}

onMounted(() => {
  initFormats()
})
</script>

<template>
  <ElContainer
    class="relative min-h-screen bg-radial from-slate-900 via-slate-800 to-slate-950 md:p-4 p-2 overflow-hidden"
    direction="vertical"
  >
    <div
      className="absolute top-0 right-0 w-[30rem] h-[30rem] bg-emerald-900 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2 z-0"
    />

    <div
      className="absolute bottom-0 left-0 w-72 h-72 bg-cyan-800 rounded-full blur-3xl -translate-x-1/3 translate-y-1/3 z-0"
    />

    <AppHeader :username="user?.username || $t('views.home.anonymous')" class="z-10" />

    <ElMain class="mt-6 md:mt-16 z-10">
      <div class="max-w-6xl mx-auto">
        <ElCard class="md:p-6 rounded-xl shadow-lg">
          <ElTabs>
            <ElTabPane>
              <template #label>
                <span>
                  <ElIcon><Upload /></ElIcon>
                  <span class="ml-2 text-md md:text-xl">
                    {{ $t('views.home.tabs.conversion') }}
                  </span>
                </span>
              </template>
              <JobUploadForm :formats="formats" :isLoadingFormats="fetchingFormats" />
            </ElTabPane>
            <ElTabPane>
              <template #label>
                <span>
                  <ElIcon><Document /></ElIcon>
                  <span class="ml-2 text-md md:text-xl">
                    {{ $t('views.home.tabs.history') }}
                  </span>
                </span>
              </template>
              <JobTable />
            </ElTabPane>
          </ElTabs>
        </ElCard>
      </div>
    </ElMain>
  </ElContainer>
</template>
