import type { UploadRawFile } from 'element-plus'

interface JobRead {
  id: number
  filename: string
  input_path: string
  output_path: string
  original_format: string
  input_size_bytes: number | null
  output_size_bytes: number | null
  target_format: string
  user_id: number
  status: string
  created_at: string
}

interface JobStatus {
  id: number
  status: string
  user_id: number
  created_at: string
  started_at: string | null
  finished_at: string | null
}

interface JobDownload {
  filename: string
  url: string
  public_url: string
}

interface JobCreate {
  target_format: string
  file: UploadRawFile | null
}

export type { JobRead, JobStatus, JobDownload, JobCreate }
