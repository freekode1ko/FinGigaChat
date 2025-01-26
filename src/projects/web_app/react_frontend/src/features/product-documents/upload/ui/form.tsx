import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  documentFormSchema,
  useUploadProductDocumentMutation,
} from '@/entities/products'
import { handleError } from '@/shared/api'
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

import { dropZoneConfig } from '../model'

export function UploadDocumentForm({
  productId,
  onSuccess,
}: {
  productId: number
  onSuccess: () => void
}) {
  const [upload, { isLoading }] = useUploadProductDocumentMutation()

  const form = useForm<z.infer<typeof documentFormSchema>>({
    resolver: zodResolver(documentFormSchema),
    disabled: isLoading,
    defaultValues: {
      name: '',
      description: '',
      files: null,
    },
  })

  const onSubmit = async (values: z.infer<typeof documentFormSchema>, callOnSuccess: boolean = false) => {
    toast.promise(
      upload({
        document: { ...values, file: values.files ? values.files[0] : null },
        productId,
      }).unwrap(),
      {
        loading: `Загружаем документ ${values.name}...`,
        success: () => {
          if (callOnSuccess) {
            onSuccess()
          }
          form.reset()
          return 'Документ успешно загружен!'
        },
        error: (error) => handleError(error),
      }
    )
  }

  return (
    <Form {...form}>
      <form className="space-y-4">

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
              <FormDescription>
                Вы можете не загружать документ, если это не требуется 
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex flex-col md:flex-row gap-2 md:justify-end">
          <Button
            className="w-full md:w-auto"
            variant="outline"
            disabled={isLoading}
            onClick={() => onSubmit(form.getValues(), false)}
          >
            Сохранить и продолжить
          </Button>
          <Button
            className="w-full md:w-auto"
            disabled={isLoading}
            onClick={() => onSubmit(form.getValues(), true)}
          >
            Сохранить
          </Button>
        </div>

      </form>
    </Form>
  )
}
