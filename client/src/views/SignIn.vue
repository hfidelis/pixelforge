<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { required, email, helpers } from '@vuelidate/validators'

import useVuelidate from '@vuelidate/core'
import LangSelect from '@/components/shared/LangSelect.vue'

const { t } = useI18n()
import { ElForm, ElFormItem, ElInput, ElButton } from 'element-plus'

const router = useRouter()
const { login, loading } = useAuth()

const form = ref({
  email: '',
  password: '',
  remember: false,
})

const rules = computed(() => ({
  email: {
    required: helpers.withMessage(t('views.signIn.form.fields.email.error.required'), required),
    email: helpers.withMessage(t('views.signIn.form.fields.email.error.invalid'), email),
  },
  password: {
    required: helpers.withMessage(t('views.signIn.form.fields.password.error.required'), required),
  },
}))

const v$ = useVuelidate(rules, form)

const handleLogin = async () => {
  const isValid = await v$.value.$validate()

  if (!isValid) {
    console.warn(v$.value.email.$errors)
    push.warning({
      title: t('views.signIn.form.error.invalid.title'),
      message: t('views.signIn.form.error.invalid.message'),
    })
    return
  }

  try {
    await login(form.value.email, form.value.password)

    push.success({
      title: t('views.signIn.form.success.title'),
      message: t('views.signIn.form.success.message'),
    })

    router.push({ name: 'home' })
  } catch {
    push.error({
      title: t('views.signIn.form.error.failed.title'),
      message: t('views.signIn.form.error.failed.message'),
    })
  }
}
</script>

<template>
  <main
    class="relative md:bg-gradient-to-br from-cyan-900 via-slate-950 to-emerald-900 flex items-center justify-center min-h-screen p-6 bg-[url('/images/signin_aside.webp')]"
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
          <h2 class="text-2xl font-semibold text-slate-200 block md:hidden">
            {{ $t('views.signIn.mobileTitle') }}
          </h2>
          <h2 class="text-2xl font-semibold text-slate-200 hidden md:block">
            {{ $t('views.signIn.title') }}
          </h2>
        </div>

        <el-form :model="form" ref="formRef" class="space-y-6" @submit.prevent="handleLogin">
          <el-form-item
            label-position="top"
            :label="$t('views.signIn.form.fields.email.label')"
            :error="v$.email.$error ? (v$.email.$errors[0]?.$message as string) : ''"
          >
            <el-input
              v-model="form.email"
              :placeholder="$t('views.signIn.form.fields.email.placeholder')"
              :disabled="loading"
              clearable
              size="large"
            />
          </el-form-item>

          <el-form-item
            :label="$t('views.signIn.form.fields.password.label')"
            label-position="top"
            :error="v$.password.$error ? (v$.password.$errors[0]?.$message as string) : ''"
          >
            <el-input
              v-model="form.password"
              :placeholder="$t('views.signIn.form.fields.password.placeholder')"
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
            @click="handleLogin"
          >
            {{ $t('views.signIn.form.submit.label') }}
          </el-button>

          <p class="text-center text-sm text-gray-600 mt-4">
            {{ $t('views.signIn.footer.noAccount') }}
            <a
              href="#"
              class="text-emerald-600 font-medium hover:underline"
              @click.prevent="router.push({ name: 'signup' })"
            >
              {{ $t('views.signIn.footer.signUp') }}
            </a>
          </p>
        </el-form>
      </div>

      <aside class="relative hidden md:block">
        <img src="/images/signin_aside.webp" alt="login" class="w-full h-full object-cover" />
        <div
          class="absolute inset-0 bg-gradient-to-b from-stone-950/60 to-slate-950 flex flex-col justify-center items-center text-white text-center p-10"
        >
          <h1 class="text-3xl font-semibold mb-4">{{ $t('views.signIn.aside.title') }}</h1>
          <p class="text-white/90 leading-relaxed font-bold">
            {{ $t('views.signIn.aside.subtitle') }}
          </p>
        </div>
      </aside>
    </section>
  </main>
</template>
