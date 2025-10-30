<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { push } from 'notivue'
import useVuelidate from '@vuelidate/core'
import { required, email, minLength, maxLength, sameAs, helpers } from '@vuelidate/validators'

import { ElForm, ElFormItem, ElInput, ElButton } from 'element-plus'
import LangSelect from '@/components/shared/LangSelect.vue'
import authService from '@/api/services/auth.service'

const { t } = useI18n()
const router = useRouter()

const loading = ref(false)
const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const rules = computed(() => ({
  username: {
    required: helpers.withMessage(t('views.signUp.form.fields.username.error.required'), required),
    minLength: helpers.withMessage(
      t('views.signUp.form.fields.username.error.minLength'),
      minLength(3),
    ),
    maxLength: helpers.withMessage(
      t('views.signUp.form.fields.username.error.maxLength'),
      maxLength(20),
    ),
  },
  email: {
    required: helpers.withMessage(t('views.signUp.form.fields.email.error.required'), required),
    email: helpers.withMessage(t('views.signUp.form.fields.email.error.invalid'), email),
  },
  password: {
    required: helpers.withMessage(t('views.signUp.form.fields.password.error.required'), required),
    minLength: helpers.withMessage(
      t('views.signUp.form.fields.password.error.minLength'),
      minLength(6),
    ),
  },
  confirmPassword: {
    required: helpers.withMessage(
      t('views.signUp.form.fields.confirmPassword.error.required'),
      required,
    ),
    sameAsPassword: helpers.withMessage(
      t('views.signUp.form.fields.confirmPassword.error.mismatch'),
      sameAs(computed(() => form.value.password)),
    ),
  },
}))

const v$ = useVuelidate(rules, form)

const handleRegister = async () => {
  const isValid = await v$.value.$validate()

  if (!isValid) {
    push.warning({
      title: t('views.signUp.form.error.invalid.title'),
      message: t('views.signUp.form.error.invalid.message'),
    })
    return
  }

  try {
    loading.value = true
    await authService.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    })

    push.success({
      title: t('views.signUp.form.success.title'),
      message: t('views.signUp.form.success.message'),
    })

    router.push({ name: 'signin' })
  } catch (error: any) {
    let title = t('views.signUp.form.error.failed.title')
    let message = t('views.signUp.form.error.failed.message')

    if (
      error?.response?.data?.detail &&
      error.response.data.detail.includes('already registered')
    ) {
      title = t('views.signUp.form.error.exists.title')
      message = t('views.signUp.form.error.exists.message')
    }

    push.error({
      title,
      message,
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main
    class="relative md:bg-gradient-to-br from-cyan-900 via-slate-950 to-emerald-900 flex items-center justify-center min-h-screen p-6 bg-[url('/images/signup_aside.webp')]"
  >
    <div class="absolute top-6 right-6">
      <LangSelect />
    </div>

    <section
      class="w-full max-w-5xl md:bg-gradient-to-b md:from-slate-900 md:to-slate-950 bg-slate-900/90 rounded-2xl shadow-xl grid md:grid-cols-2 overflow-hidden"
    >
      <div class="p-8 lg:p-12 flex flex-col justify-center">
        <div class="mb-8 text-center">
          <img src="/images/logo.webp" alt="logo" class="mx-auto w-25 mb-4" />
          <h2 class="text-2xl font-semibold text-slate-200">
            {{ $t('views.signUp.title') }}
          </h2>
        </div>

        <el-form :model="form" class="space-y-6" @submit.prevent="handleRegister">
          <el-form-item
            :label="$t('views.signUp.form.fields.username.label')"
            label-position="top"
            :error="v$.username.$error ? (v$.username.$errors[0]?.$message as string) : ''"
          >
            <el-input
              v-model="form.username"
              :placeholder="$t('views.signUp.form.fields.username.placeholder')"
              :disabled="loading"
              clearable
              size="large"
            />
          </el-form-item>

          <el-form-item
            :label="$t('views.signUp.form.fields.email.label')"
            label-position="top"
            :error="v$.email.$error ? (v$.email.$errors[0]?.$message as string) : ''"
          >
            <el-input
              v-model="form.email"
              :placeholder="$t('views.signUp.form.fields.email.placeholder')"
              :disabled="loading"
              clearable
              size="large"
            />
          </el-form-item>

          <el-form-item
            :label="$t('views.signUp.form.fields.password.label')"
            label-position="top"
            :error="v$.password.$error ? (v$.password.$errors[0]?.$message as string) : ''"
          >
            <el-input
              v-model="form.password"
              :placeholder="$t('views.signUp.form.fields.password.placeholder')"
              :type="'password'"
              show-password
              size="large"
              :disabled="loading"
            />
          </el-form-item>

          <el-form-item
            :label="$t('views.signUp.form.fields.confirmPassword.label')"
            label-position="top"
            :error="
              v$.confirmPassword.$error ? (v$.confirmPassword.$errors[0]?.$message as string) : ''
            "
          >
            <el-input
              v-model="form.confirmPassword"
              :placeholder="$t('views.signUp.form.fields.confirmPassword.placeholder')"
              :type="'password'"
              show-password
              size="large"
              :disabled="loading"
            />
          </el-form-item>

          <el-button
            class="w-full !h-12 !text-base mt-4"
            color="#10B981"
            :loading="loading"
            @click="handleRegister"
          >
            {{ $t('views.signUp.form.submit.label') }}
          </el-button>

          <p class="text-center text-sm text-gray-600 mt-4">
            {{ $t('views.signUp.footer.alreadyAccount') }}
            <a
              href="#"
              class="text-emerald-600 font-medium hover:underline"
              @click.prevent="router.push({ name: 'signin' })"
            >
              {{ $t('views.signUp.footer.signIn') }}
            </a>
          </p>
        </el-form>
      </div>

      <aside class="relative hidden md:block">
        <img src="/images/signup_aside.webp" alt="signup" class="w-full h-full object-cover" />
        <div
          class="absolute inset-0 bg-gradient-to-b from-stone-950/60 to-slate-950 flex flex-col justify-center items-center text-white text-center p-10"
        >
          <h1 class="text-3xl font-semibold mb-4">{{ $t('views.signUp.aside.title') }}</h1>
          <p class="text-white/90 leading-relaxed font-bold">
            {{ $t('views.signUp.aside.subtitle') }}
          </p>
        </div>
      </aside>
    </section>
  </main>
</template>
