import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useUploadProductDocumentMutation } from '@/entities/products'
import { FileUploadField } from '@/shared/kit'
import {
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Textarea,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

const formSchema = z.object({
  name: z.string(),
  description: z.string().optional(),
  files: z
    .array(
      z.instanceof(File).refine((file) => file.size < 20 * 1024 * 1024, {
        message: 'Размер файла должен быть меньше 20MB',
      })
    )
    .max(1, {
      message: 'Вы не можете прикрепить больше 1 файла',
    }),
})

export function UploadDocumentForm({ productId, onSuccess }: { productId: number, onSuccess: () => void }) {
  const [upload] = useUploadProductDocumentMutation()
  const dropZoneConfig = {
    maxFiles: 1,
    maxSize: 1024 * 1024 * 20, // 20 MB
    multiple: false,
    accept: {
      'application/pdf': ['.pdf'],
    },
  }

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    toast.promise(
      upload({
        document: { ...values, file: values.files[0] },
        productId,
      }).unwrap(),
      {
        loading: `Загружаем документ ${values.name}...`,
        success: 'Документ успешно загружен!',
        error: 'Мы не смогли загрузить документ. Попробуйте позже.',
      }
    )
    onSuccess()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Название документа</FormLabel>
              <FormControl>
                <Input placeholder="Отчет за 2024 год" type="" {...field} />
              </FormControl>
              <FormDescription>
                Будет отображаться в списке документов
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Описание документа</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Документ содержит информацию по основным направлениям работы за 2024 год."
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="files"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Выберите документ</FormLabel>
              <FormControl>
                <FileUploadField
                  value={field.value}
                  onValueChange={field.onChange}
                  dropzoneOptions={dropZoneConfig}
                  helpText="Только .PDF документы"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full">
          Сохранить
        </Button>
      </form>
    </Form>
  )
}
