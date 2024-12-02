import { CloudUpload, Paperclip } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useUploadProductDocumentMutation } from '@/entities/products'
import {
  Button,
  FileInput,
  FileUploader,
  FileUploaderContent,
  FileUploaderItem,
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

export function UploadDocumentForm({ productId }: { productId: number }) {
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
                <FileUploader
                  value={field.value}
                  onValueChange={field.onChange}
                  dropzoneOptions={dropZoneConfig}
                  className="relative bg-background rounded-lg p-2"
                >
                  <FileInput
                    id="fileInput"
                    className="outline-dashed outline-1 outline-slate-500"
                  >
                    <div className="flex items-center justify-center flex-col p-8 w-full ">
                      <CloudUpload className="text-muted w-10 h-10" />
                      <p className="mb-1 text-sm text-muted text-center">
                        <span className="font-semibold">
                          Кликните для загрузки
                        </span>
                        <br />
                        или перетащите сюда файл
                      </p>
                      <p className="text-xs text-foreground">
                        Только .PDF документы
                      </p>
                    </div>
                  </FileInput>
                  <FileUploaderContent>
                    {field.value &&
                      field.value.length > 0 &&
                      field.value.map((file, idx) => (
                        <FileUploaderItem key={idx} index={idx}>
                          <Paperclip className="h-4 w-4 stroke-current" />
                          <span>{file.name}</span>
                        </FileUploaderItem>
                      ))}
                  </FileUploaderContent>
                </FileUploader>
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
