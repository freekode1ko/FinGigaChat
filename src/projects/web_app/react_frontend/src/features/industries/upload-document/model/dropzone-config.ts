import { MAX_INDUSTRY_DOCUMENT_SIZE_MB } from '@/entities/industries'

const dropZoneConfig = {
  maxFiles: 1,
  maxSize: 1024 * 1024 * MAX_INDUSTRY_DOCUMENT_SIZE_MB,
  multiple: false,
  accept: {
    'application/pdf': ['.pdf'],
  },
}

export { dropZoneConfig }
