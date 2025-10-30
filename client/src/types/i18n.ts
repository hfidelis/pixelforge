// eslint-disable-next-line @typescript-eslint/no-unused-vars
const Locales = {
  ptBR: 'pt-BR',
  enUS: 'en-US',
} as const

type Locale = (typeof Locales)[keyof typeof Locales]

export type { Locale }
