export interface PaginatedResponse<T> {
  results: T[]
  count: number
  page: number
  size: number
  next_url: string | null
  prev_url: string | null
}
