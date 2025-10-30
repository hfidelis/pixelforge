<script setup lang="ts">
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'
import { ref, reactive, watch, computed, onBeforeUnmount } from 'vue'
import { Upload, Document, Delete, FolderChecked, Picture, Download } from '@element-plus/icons-vue'
import VueEasyLightbox from 'vue-easy-lightbox'

import type { JobRead, JobCreate } from '@/types/job'
import type { UploadUserFile } from 'element-plus'
import useVuelidate from '@vuelidate/core'
import { required } from '@vuelidate/validators'

import jobService from '@/api/services/job.service'
import { bytesToMB } from '@/utils'

interface JobUploadFormProps {
  formats: string[]
  isLoadingFormats: boolean
}

const props = defineProps<JobUploadFormProps>()
const { t } = useI18n()

const isUploadMode = ref(true)
const isUploading = ref(false)
const currentJob = ref<JobRead | null>(null)

const socket = ref<WebSocket | null>(null)
const isConnected = ref(false)

const lightboxVisible = ref(false)
const lightboxImgs = ref<string[]>([])
const lightboxIndex = ref(0)

const form = reactive<JobCreate>({
  target_format: '',
  file: null,
})

const rules = { target_format: { required }, file: { required } }
const v$ = useVuelidate(rules, form)
const fileList = ref<UploadUserFile[]>([])

const isUploadDisabled = computed(() => isUploading.value || fileList.value.length !== 0)

watch(
  () => props.formats,
  (newFormats) => {
    if (newFormats.length && !form.target_format) {
      form.target_format = newFormats[0]!
    }
  },
  { immediate: true },
)

const onFileChange = (fileItem: UploadUserFile) => {
  if (form.file) {
    push.warning({
      title: t('components.jobs.jobUploadForm.messages.fileAlreadySelected'),
      message: t('components.jobs.jobUploadForm.messages.removeFirst'),
    })
    return false
  }

  const ext = (fileItem.name.split('.').pop() || '').toLowerCase()
  if (props.formats.length && !props.formats.includes(ext)) {
    push.warning({
      title: t('components.jobs.jobUploadForm.messages.invalidFormat'),
      message: t('components.jobs.jobUploadForm.messages.formatNotAccepted', {
        ext,
        formats: props.formats.join(', '),
      }),
    })
    return false
  }

  form.file = fileItem.raw!
  fileList.value = [fileItem]
  return false
}

const removeFile = () => {
  form.file = null
  fileList.value = []
}

const connectWebSocket = (jobId: number) => {
  const baseApiUrl = import.meta.env.VITE_API_BASE_URL
  const wsBaseUrl = baseApiUrl.replace(/^http/, 'ws')
  const cleanBase = wsBaseUrl.replace(/\/$/, '')
  const wsUrl = `${cleanBase}/ws/jobs/${jobId}`

  socket.value = new WebSocket(wsUrl)

  socket.value.onopen = () => {
    isConnected.value = true
  }

  socket.value.onmessage = async (event) => {
    const data = JSON.parse(event.data)

    if (data.status) {
      currentJob.value = { ...currentJob.value!, status: data.status }

      if (data.status === 'SUCCESS') {
        push.success({
          title: t('components.jobs.jobUploadForm.messages.conversionComplete'),
          message: t('components.jobs.jobUploadForm.messages.conversionSuccess'),
        })
      } else if (data.status === 'FAILED') {
        push.error({
          title: t('components.jobs.jobUploadForm.messages.conversionFailed'),
          message: t('components.jobs.jobUploadForm.messages.conversionError'),
        })
      }
    }
  }

  socket.value.onclose = () => {
    isConnected.value = false
  }

  socket.value.onerror = () => {
    push.error({
      title: t('components.jobs.jobUploadForm.messages.connectionError'),
      message: t('components.jobs.jobUploadForm.messages.connectionMessage'),
    })
    socket.value?.close()
    isConnected.value = false
  }
}

onBeforeUnmount(() => {
  if (socket.value) socket.value.close()
})

const submit = async () => {
  await v$.value.$validate()

  if (v$.value.$error || !form.file) {
    push.warning({
      title: t('components.jobs.jobUploadForm.messages.invalidFields'),
      message: t('components.jobs.jobUploadForm.messages.checkFields'),
    })
    return
  }

  const fileName = form.file.name
  const ext = (fileName.split('.').pop() || '').toLowerCase()

  if (ext === form.target_format.toLowerCase()) {
    push.warning({
      title: t('components.jobs.jobUploadForm.messages.error'),
      message: t('components.jobs.jobUploadForm.messages.sameFormatMessage'),
    })
    return
  }

  isUploading.value = true

  try {
    const payload = { target_format: form.target_format, file: form.file }
    const created = await jobService.createJob(payload)

    push.success({
      title: t('components.jobs.jobUploadForm.messages.uploadSent'),
      message: t('components.jobs.jobUploadForm.messages.jobCreated'),
    })

    currentJob.value = created
    isUploadMode.value = false
    connectWebSocket(created.id)
  } catch {
    push.error({
      title: t('components.jobs.jobUploadForm.messages.error'),
      message: t('components.jobs.jobUploadForm.messages.uploadError'),
    })
  } finally {
    isUploading.value = false
  }
}

const handlePreview = async () => {
  if (!currentJob.value) return
  try {
    const blobUrl = await jobService.getJobPreviewBlob(currentJob.value.id)
    lightboxImgs.value = [blobUrl]
    lightboxVisible.value = true
    push.success({
      title: t('components.jobs.jobUploadForm.messages.previewSuccess'),
      message: t('components.jobs.jobUploadForm.messages.previewMessage'),
    })
  } catch {
    push.error({
      title: t('components.jobs.jobUploadForm.messages.previewErrorTitle'),
      message: t('components.jobs.jobUploadForm.messages.previewErrorMessage'),
    })
  }
}

const handleDownload = async () => {
  if (!currentJob.value) return
  try {
    const filename = `${currentJob.value.filename.split('.')[0]}.${currentJob.value.target_format}`
    await jobService.downloadJob(currentJob.value.id, filename)
    push.success({
      title: t('components.jobs.jobUploadForm.messages.downloadStart'),
      message: t('components.jobs.jobUploadForm.messages.downloadSuccess'),
    })
  } catch {
    push.error({
      title: t('components.jobs.jobUploadForm.messages.downloadError'),
      message: t('components.jobs.jobUploadForm.messages.downloadErrorMessage'),
    })
  }
}

const onHideLightbox = () => {
  lightboxVisible.value = false
  if (lightboxImgs.value.length) {
    URL.revokeObjectURL(lightboxImgs.value[0]!)
  }
}

const handleReset = () => {
  currentJob.value = null
  form.target_format = props.formats.length ? props.formats[0]! : ''
  form.file = null
  fileList.value = []
  if (socket.value) {
    socket.value.close()
    socket.value = null
    isConnected.value = false
  }
  isUploadMode.value = true
}

const mapStatusToText = (status: string): string => {
  return t(`components.jobs.jobUploadForm.status.${status.toLowerCase()}`) as string
}
</script>

<template>
  <!-- Upload mode -->
  <section v-if="isUploadMode">
    <h2 class="text-2xl font-semibold mb-2">
      {{ t('components.jobs.jobUploadForm.title.upload') }}
    </h2>
    <p class="text-md md:text-sm text-slate-300 mb-4">
      {{ t('components.jobs.jobUploadForm.description.upload') }}
      <span class="font-medium ml-1">
        {{ t('components.jobs.jobUploadForm.description.supportedFormats') }}:
        {{ props.formats.join(', ') || 'carregando...' }}
      </span>
    </p>

    <ElForm label-position="top" class="space-y-4">
      <ElFormItem :label="t('components.jobs.jobUploadForm.labels.targetFormat')">
        <ElSelect
          v-model="form.target_format"
          :placeholder="t('components.jobs.jobUploadForm.labels.targetFormat')"
          :loading="isLoadingFormats"
          :disabled="isLoadingFormats"
          class="w-full"
        >
          <ElOption
            v-for="fmt in props.formats"
            :key="fmt"
            :label="fmt.toUpperCase()"
            :value="fmt"
          />
        </ElSelect>
      </ElFormItem>

      <ElFormItem :label="t('components.jobs.jobUploadForm.labels.file')">
        <ElUpload
          drag
          v-model:file-list="fileList"
          :on-change="onFileChange"
          :auto-upload="false"
          :show-file-list="false"
          :on-remove="removeFile"
          action="#"
          :limit="1"
          :disabled="isUploadDisabled"
          accept="image/*"
          class="w-full"
        >
          <ElIcon><FolderChecked v-if="isUploadDisabled" /><Upload v-else /></ElIcon>
          <div class="el-upload__text">
            <template v-if="isUploadDisabled">
              {{ t('components.jobs.jobUploadForm.messages.removeFirst') }}
            </template>
            <template v-else>
              {{ t('components.jobs.jobUploadForm.messages.dragOrClick') }}
            </template>
          </div>
        </ElUpload>

        <div v-if="form.file" :key="form.file.name" class="mt-2 flex items-center gap-3">
          <ElIcon><Document /></ElIcon>
          <div class="text-sm">{{ form.file.name }}</div>
          <ElButton type="text" size="small" @click="removeFile">
            {{ t('components.jobs.jobUploadForm.buttons.remove') }}
          </ElButton>
        </div>
      </ElFormItem>

      <div class="flex items-center gap-3 mt-4 justify-between md:justify-start">
        <ElButton color="#10B981" :loading="isUploading" @click="submit">
          <ElIcon><Upload /></ElIcon>
          <span class="ml-2">{{ t('components.jobs.jobUploadForm.buttons.upload') }}</span>
        </ElButton>
        <ElButton type="warning" plain @click="removeFile">
          <ElIcon><Delete /></ElIcon>
          <span class="ml-2">{{ t('components.jobs.jobUploadForm.buttons.clear') }}</span>
        </ElButton>
      </div>
    </ElForm>
  </section>

  <!-- Job info mode -->
  <section
    v-else
    class="bg-gradient-to-br from-slate-800/70 via-slate-900/80 to-slate-950 rounded-2xl p-6 md:p-10 shadow-lg border border-slate-700/40 transition-all duration-300"
  >
    <div class="flex flex-col items-start gap-4 w-full">
      <h2 class="text-2xl md:text-3xl font-bold text-emerald-400 tracking-tight">
        ✅ {{ t('components.jobs.jobUploadForm.title.success') }}
      </h2>

      <div class="w-full space-y-3 text-slate-300 text-base md:text-lg">
        <div class="flex flex-wrap justify-between gap-y-2">
          <p class="font-medium">{{ t('components.jobs.jobUploadForm.labels.id') }}:</p>
          <span class="font-mono text-emerald-200">{{ currentJob?.id }}</span>
        </div>

        <div class="flex flex-wrap justify-between gap-y-2">
          <p class="font-medium">{{ t('components.jobs.jobUploadForm.labels.format') }}:</p>
          <span class="font-mono text-emerald-200">
            {{ currentJob?.original_format.toUpperCase() }} →
            {{ currentJob?.target_format.toUpperCase() }}
          </span>
        </div>

        <div class="flex flex-wrap justify-between gap-y-2">
          <p class="font-medium">{{ t('components.jobs.jobUploadForm.labels.filename') }}:</p>
          <span class="font-mono text-emerald-200 break-all">{{ currentJob?.filename }}</span>
        </div>

        <div class="flex flex-wrap justify-between gap-y-2 items-center">
          <p class="font-medium">{{ t('components.jobs.jobUploadForm.labels.status') }}:</p>
          <span
            :class="{
              'text-yellow-400 animate-pulse': currentJob?.status === 'PROCESSING',
              'text-green-400': currentJob?.status === 'SUCCESS',
              'text-red-400': currentJob?.status === 'FAILED',
              'text-slate-400': currentJob?.status === 'PENDING',
            }"
            class="font-mono text-sm md:text-base font-semibold ms-1"
          >
            {{ mapStatusToText(currentJob?.status!) }}
          </span>
        </div>

        <div class="flex flex-wrap justify-between gap-y-2">
          <p class="font-medium">{{ t('components.jobs.jobUploadForm.labels.inputSize') }}:</p>
          <span class="font-mono font-medium text-emerald-200">
            {{ bytesToMB(currentJob?.input_size_bytes!) }} MB
          </span>
        </div>
      </div>

      <transition name="fade">
        <div v-if="!isConnected" class="text-yellow-400 text-sm md:text-base mt-3">
          {{ t('components.jobs.jobUploadForm.description.connecting') }}
        </div>
      </transition>

      <div
        v-if="currentJob?.status === 'SUCCESS'"
        class="mt-6 flex flex-col sm:flex-row gap-3 w-full justify-start sm:justify-center"
      >
        <ElButton
          color="#10B981"
          class="flex-1 sm:flex-none w-full sm:w-auto !m-0"
          @click="handlePreview"
        >
          <ElIcon><Picture /></ElIcon>
          <span class="ml-2 font-medium">{{
            t('components.jobs.jobUploadForm.buttons.view')
          }}</span>
        </ElButton>

        <ElButton
          color="#3B82F6"
          class="flex-1 sm:flex-none w-full sm:w-auto !m-0"
          @click="handleDownload"
        >
          <ElIcon><Download /></ElIcon>
          <span class="ml-2 font-medium">{{
            t('components.jobs.jobUploadForm.buttons.download')
          }}</span>
        </ElButton>

        <ElButton
          color="#6366F1"
          plain
          class="flex-1 sm:flex-none w-full sm:w-auto !m-0"
          @click="handleReset"
        >
          {{ t('components.jobs.jobUploadForm.buttons.new') }}
        </ElButton>
      </div>

      <p v-else class="text-md text-slate-400 mt-6 text-center w-full italic tracking-wide">
        {{ t('components.jobs.jobUploadForm.description.waiting') }}
      </p>
    </div>

    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImgs"
      :index="lightboxIndex"
      @hide="onHideLightbox"
    />
  </section>
</template>
