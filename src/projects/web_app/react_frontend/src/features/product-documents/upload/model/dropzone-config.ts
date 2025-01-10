import { MAX_PRODUCT_DOCUMENT_SIZE_MB } from '@/entities/products/model/constants'

const dropZoneConfig = {
  maxFiles: 1,
  maxSize: 1024 * 1024 * MAX_PRODUCT_DOCUMENT_SIZE_MB,
  multiple: false,
  accept: {
    'application/pdf': ['.pdf'],
  },
}

export { dropZoneConfig }
