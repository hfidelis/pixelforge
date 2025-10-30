import type { Locale } from '@/types/i18n'
import { createI18n, type I18nOptions } from 'vue-i18n'

import ptBR from '@/locales/pt-BR.json'
import enUS from '@/locales/en-US.json'

const messages = {
  'pt-BR': ptBR,
  'en-US': enUS,
}

const defaultLocale: Locale = 'pt-BR'

const options: I18nOptions = {
  fallbackLocale: defaultLocale,
  globalInjection: true,
  locale: defaultLocale,
  legacy: false,
  messages,
}

const i18n = createI18n(options)

export default i18n
