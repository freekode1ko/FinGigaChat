import { z } from 'zod'

const fileSchema = (maxSizeMB = 20) =>
  z
    .array(
      z.instanceof(File).refine((file) => file.size < maxSizeMB * 1024 * 1024, {
        message: `Размер файла должен быть меньше ${maxSizeMB}MB`,
      })
    )
    .max(1, {
      message: 'Вы не можете прикрепить больше 1 файла',
    })

export { fileSchema }
