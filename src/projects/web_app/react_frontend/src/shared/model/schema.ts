import { z } from 'zod'

const fileSchema = (maxSizeMB = 20, maxFiles = 1) =>
  z
    .array(
      z.instanceof(File).refine((file) => file.size < maxSizeMB * 1024 * 1024, {
        message: `Размер файла должен быть меньше ${maxSizeMB}MB`,
      })
    )
    .max(maxFiles, {
      message: `Вы не можете прикрепить больше ${maxFiles} файлов`,
    })

export { fileSchema }
