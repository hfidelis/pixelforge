<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'
import { Picture, Download, Refresh } from '@element-plus/icons-vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import jobService from '@/api/services/job.service'
import type { JobRead } from '@/types/job'
import type { PaginatedResponse } from '@/types/util'

const { t } = useI18n()

const jobs = ref<JobRead[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

const lightboxVisible = ref(false)
const lightboxImgs = ref<string[]>([])
const lightboxIndex = ref(0)

const fetchJobs = async () => {
  loading.value = true
  try {
    const data: PaginatedResponse<JobRead> = await jobService.getJobs(
      currentPage.value,
      pageSize.value,
    )
    jobs.value = data.results
    totalItems.value = data.count
  } catch {
    push.error({
      title: t('components.jobs.jobTable.messages.loadErrorTitle'),
      message: t('components.jobs.jobTable.messages.loadErrorMessage'),
    })
  } finally {
    loading.value = false
  }
}

onMounted(fetchJobs)

const handlePageChange = async (page: number) => {
  currentPage.value = page
  await fetchJobs()
}

const handleRefresh = async () => {
  await fetchJobs()
  push.success({
    title: t('components.jobs.jobTable.messages.refreshSuccessTitle'),
    message: t('components.jobs.jobTable.messages.refreshSuccessMessage'),
  })
}

const handlePreview = async (job: JobRead) => {
  try {
    const blobUrl = await jobService.getJobPreviewBlob(job.id)
    lightboxImgs.value = [blobUrl]
    lightboxVisible.value = true
  } catch {
    push.error({
      title: t('components.jobs.jobTable.messages.previewErrorTitle'),
      message: t('components.jobs.jobTable.messages.previewErrorMessage'),
    })
  }
}

const handleDownload = async (job: JobRead) => {
  try {
    const filename = `${job.filename.split('.')[0]}.${job.target_format}`
    await jobService.downloadJob(job.id, filename)
    push.success({
      title: t('components.jobs.jobTable.messages.downloadSuccessTitle'),
      message: t('components.jobs.jobTable.messages.downloadSuccessMessage'),
    })
  } catch {
    push.error({
      title: t('components.jobs.jobTable.messages.downloadErrorTitle'),
      message: t('components.jobs.jobTable.messages.downloadErrorMessage'),
    })
  }
}

const formatDate = (isoDate: string) => {
  return new Date(isoDate).toLocaleString()
}

const truncateColumn = (text: string, length = 20) => {
  return text.length > length ? text.slice(0, length) + '...' : text
}
</script>

<template>
  <section class="transition-all duration-300">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl md:text-3xl font-bold text-emerald-400 tracking-tight">
        {{ t('components.jobs.jobTable.title') }}
      </h2>
      <ElButton
        :icon="Refresh"
        color="#10B981"
        plain
        size="large"
        :loading="loading"
        @click="handleRefresh"
      >
        {{ t('components.jobs.jobTable.buttons.refresh') }}
      </ElButton>
    </div>

    <ElTable
      :data="jobs"
      v-loading="loading"
      class="w-full rounded-lg overflow-hidden"
      header-cell-class-name="bg-slate-800 text-slate-100 font-semibold"
    >
      <ElTableColumn prop="id" :label="t('components.jobs.jobTable.columns.id')" width="80" />
      <ElTableColumn prop="filename" :label="t('components.jobs.jobTable.columns.filename')">
        <template #default="{ row }">{{ truncateColumn(row.filename, 15) }}</template>
      </ElTableColumn>
      <ElTableColumn
        prop="created_at"
        :label="t('components.jobs.jobTable.columns.createdAt')"
        width="200"
      >
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </ElTableColumn>

      <ElTableColumn
        prop="original_format"
        :label="t('components.jobs.jobTable.columns.originalFormat')"
        width="120"
      >
        <template #default="{ row }">{{ row.original_format?.toUpperCase() }}</template>
      </ElTableColumn>

      <ElTableColumn
        prop="target_format"
        :label="t('components.jobs.jobTable.columns.targetFormat')"
        width="120"
      >
        <template #default="{ row }">{{ row.target_format?.toUpperCase() }}</template>
      </ElTableColumn>

      <ElTableColumn
        prop="status"
        :label="t('components.jobs.jobTable.columns.status')"
        width="140"
      >
        <template #default="{ row }">
          <span
            :class="{
              'text-yellow-400 animate-pulse': row.status === 'PROCESSING',
              'text-green-400': row.status === 'SUCCESS',
              'text-red-400': row.status === 'FAILED',
              'text-slate-400': row.status === 'PENDING',
            }"
            class="font-mono font-semibold"
          >
            {{ t(`components.jobs.jobUploadForm.status.${row.status.toLowerCase()}`) }}
          </span>
        </template>
      </ElTableColumn>

      <ElTableColumn
        :label="t('components.jobs.jobTable.columns.actions')"
        width="180"
        align="center"
      >
        <template #default="{ row }">
          <div class="flex justify-center gap-2">
            <ElButton size="small" type="success" :icon="Picture" plain @click="handlePreview(row)">
            </ElButton>
            <ElButton
              size="small"
              type="primary"
              :icon="Download"
              plain
              @click="handleDownload(row)"
            >
            </ElButton>
          </div>
        </template>
      </ElTableColumn>
    </ElTable>

    <div class="mt-6 flex justify-center">
      <ElPagination
        background
        layout="prev, pager, next"
        :page-size="pageSize"
        :total="totalItems"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>

    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImgs"
      :index="lightboxIndex"
      @hide="() => (lightboxVisible = false)"
    />
  </section>
</template>
