import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  documentFormSchema,
  useUploadIndustryDocumentMutation,
} from '@/entities/industries'
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

  const onSubmit = (values: z.infer<typeof documentFormSchema>, callOnSuccess: boolean) => {
    toast.promise(
      upload({
        document: { ...values, file: values.files[0] },
        industryId,
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
