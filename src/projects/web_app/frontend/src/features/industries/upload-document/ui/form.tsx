import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  documentFormSchema,
  useUploadIndustryDocumentMutation,
} from '@/entities/industries'
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
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { dropZoneConfig } from '../model'

export function UploadIndustryDocumentForm({
  industryId,
  onSuccess,
}: {
  industryId: number
  onSuccess: () => void
}) {
  const [upload, { isLoading }] = useUploadIndustryDocumentMutation()

  const form = useForm<z.infer<typeof documentFormSchema>>({
    disabled: isLoading,
    resolver: zodResolver(documentFormSchema),
  })

  const onSubmit = (values: z.infer<typeof documentFormSchema>) => {
    toast.promise(
      upload({
        document: { ...values, file: values.files[0] },
        industryId,
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
                <Input
                  placeholder="Данные по нефти за 2024 год"
                  type=""
                  {...field}
                />
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
        <Button type="submit" className="w-full" disabled={isLoading}>
          Сохранить
        </Button>
      </form>
    </Form>
  )
}
