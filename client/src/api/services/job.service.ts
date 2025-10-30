import axiosService from '@/api/core/axios.service'
import type { AxiosInstance } from 'axios'
import type { JobRead, JobDownload, JobCreate } from '@/types/job'
import type { PaginatedResponse } from '@/types/util'

class JobService {
  private static instance: JobService
  private axios: AxiosInstance

  private constructor() {
    this.axios = axiosService.getAxios()
  }

  public static getInstance(): JobService {
    if (!JobService.instance) {
      JobService.instance = new JobService()
    }
    return JobService.instance
  }

  async getJobs(page: number = 1, size: number = 10): Promise<PaginatedResponse<JobRead>> {
    const { data } = await this.axios.get('job', {
      params: {
        page,
        size,
      },
    })
    return data
  }

  async getJobImageFormats(): Promise<string[]> {
    const { data } = await this.axios.get<string[]>('format/image')
    return data
  }

  async createJob(job: JobCreate): Promise<JobRead> {
    const formData = new FormData()
    formData.append('target_format', job.target_format)
    formData.append('file', job.file!)
    const { data } = await this.axios.post<JobRead>('job/convert', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  }

  async getJobStatus(jobId: number): Promise<JobRead> {
    const { data } = await this.axios.get<JobRead>(`job/status/${jobId}`)
    return data
  }

  async getJobDownloadUrl(jobId: number): Promise<JobDownload> {
    const { data } = await this.axios.get<JobDownload>(`job/download/${jobId}`)
    return data
  }

  async downloadJob(jobId: number, filename: string): Promise<void> {
    const response = await this.axios.get(`job/download/${jobId}`, {
      responseType: 'blob',
    })

    const blob = new Blob([response.data])
    const link = document.createElement('a')

    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()

    URL.revokeObjectURL(link.href)
  }

  async getJobPreviewBlob(jobId: number): Promise<string> {
    const response = await this.axios.get(`job/preview/${jobId}`, {
      responseType: 'blob',
    })

    const blobUrl = URL.createObjectURL(response.data)
    return blobUrl
  }
}

const jobService = JobService.getInstance()
export default jobService
