const dropZoneConfig = {
  maxFiles: 10,
  maxSize: 1024 * 1024 * 10,
  multiple: true,
  accept: {
    'application/pdf': ['.pdf'],
    'image/*': ['.jpg', '.jpeg', '.png'],
  },
}

export { dropZoneConfig }
