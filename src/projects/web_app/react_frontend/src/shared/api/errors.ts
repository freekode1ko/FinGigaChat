import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'

const UNKNOWN_ERROR =
  'Произошла неизвестная ошибка. Пожалуйста, перезагрузите страницу и попробуйте снова.'

const VALIDATION_ERROR =
  'Ошибка валидации данных. Пожалуйста, проверьте введенные данные.'

/*
  Обработчик ошибок для RTK Query. Ошибки могут быть как от RTK Query, так и от сервера.
  Возвращает строку с текстом ошибки.
*/
export const handleError = (
  error: FetchBaseQueryError | SerializedError
): string => {
  if ('status' in error) {
    if (typeof error.status === 'number') {
      const errData = error.data as { detail?: string }
      return errData?.detail || VALIDATION_ERROR
    } else {
      return error.error
    }
  } else {
    return error.message || UNKNOWN_ERROR
  }
}
