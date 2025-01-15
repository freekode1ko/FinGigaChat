export const getDefaultFormData = (
  client: Optional<string> = null,
  description: Optional<string> = null
) => {
  return {
    client: client ? client : 'Моя новая заметка',
    description: description ? description : '',
  }
}
