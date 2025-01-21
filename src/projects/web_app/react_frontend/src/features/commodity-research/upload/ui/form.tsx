import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  analyticsFormSchema,
  useUploadCommodityResearchMutation,
} from '@/entities/commodity'
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

export function UploadResearchForm({
  commodityId,
  onSuccess,
}: {
  commodityId: number
  onSuccess: () => void
}) {
  const [upload, { isLoading }] = useUploadCommodityResearchMutation()

  const form = useForm<z.infer<typeof analyticsFormSchema>>({
    resolver: zodResolver(analyticsFormSchema),
    disabled: isLoading,
    defaultValues: {
      files: null,
    },
  })

  const onSubmit = (values: z.infer<typeof analyticsFormSchema>, callOnSuccess: boolean = false) => {
    toast.promise(
      upload({
        research: { ...values, file: values.files ? values.files[0] : null },
        commodityId,
      }).unwrap(),
      {
        loading: `Загружаем аналитику ${values.title ?? ''}...`,
        success: () => {
          if (callOnSuccess) {
            onSuccess()
          }
          form.reset()
          return 'Аналитика успешно загружена!'
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
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Название аналитики</FormLabel>
              <FormControl>
                <Input placeholder="Бензин 2024" type="" {...field} />
              </FormControl>
              <FormDescription>
                Название будет отображаться в списке, указывать необязательно
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="text"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Текст документа</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="В 2024 году нефтегазовая отрасль..."
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
              <FormLabel>Выберите файл аналитики</FormLabel>
              <FormControl>
                <FileUploadField
                  value={field.value}
                  onValueChange={field.onChange}
                  dropzoneOptions={dropZoneConfig}
                  helpText="Только .PDF документы"
                />
              </FormControl>
              <FormDescription>
                Вы можете не добавлять документ с аналитикой, если это не требуется
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
