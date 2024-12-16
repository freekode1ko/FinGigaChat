import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useUploadCommodityResearchMutation } from '@/entities/commodity'
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
  title: z.string().optional(),
  text: z.string(),
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

export function UploadResearchForm({ commodityId }: { commodityId: number }) {
  const [upload] = useUploadCommodityResearchMutation()
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
        research: { ...values, file: values.files[0] },
        commodityId,
      }).unwrap(),
      {
        loading: `Загружаем исследование ${values.title ?? ''}...`,
        success: 'Исследование успешно загружено!',
        error: 'Мы не смогли загрузить исследование. Попробуйте позже.',
      }
    )
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
