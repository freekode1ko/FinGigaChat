import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useSendMessageMutation } from '@/entities/bot'
import { useGetUserRolesQuery } from '@/entities/user'
import { RichTextEditor } from '@/shared/kit/markdown-editor'
import {
  Button,
  Checkbox,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Label,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

const formSchema = z.object({
  message: z
    .string()
    .min(20, { message: 'Текст рассылки не может быть таким коротким' }),
  role_ids: z
    .array(z.number())
    .min(1, { message: 'Необходимо выбрать хотя бы одну роль' }),
})

const SendMessageForm = () => {
  const { data: roles } = useGetUserRolesQuery()
  const [send, { isLoading }] = useSendMessageMutation()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    disabled: isLoading,
    defaultValues: {
      message: '',
      role_ids: [1],
    },
  })

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    console.log(values)
    toast.promise(send(values), {
      loading: 'Запускаем рассылку...',
      success: () => {
        form.reset()
        return 'Рассылка успешно запущена!'
      },
      error: 'Ошибка при запуске рассылки',
    })
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Текст рассылки</FormLabel>
              <FormControl>
                <RichTextEditor {...field} />
              </FormControl>
              <FormDescription>
                Не вставляйте собственные HTML или Markdown теги, используйте
                этот редактор для форматирования текста
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role_ids"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Получатели</FormLabel>
              <div
                role="group"
                className="flex flex-col md:flex-row gap-2 md:gap-4"
                tabIndex={0}
              >
                {roles?.map((role) => (
                  <div key={role.id} className="flex items-center gap-2">
                    <Checkbox
                      id={role.name}
                      checked={field.value.includes(role.id)}
                      onCheckedChange={() => {
                        field.onChange(
                          field.value.includes(role.id)
                            ? field.value.filter((id) => id !== role.id)
                            : [...field.value, role.id]
                        )
                      }}
                      value={role.id.toString()}
                    />
                    <Label htmlFor={role.name}>{role.name}</Label>
                  </div>
                ))}
              </div>
              <FormDescription>
                Укажите пользовательские роли, которым будет отправлена эта
                рассылка
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-4 flex-col md:gap-2 md:flex-row-reverse">
          <Button className="w-full md:w-auto" type="submit" disabled={false}>
            Отправить
          </Button>
          <Button
            className="w-full md:w-auto"
            type="button"
            variant="outline"
            onClick={() => form.reset()}
            disabled={false}
          >
            Очистить
          </Button>
        </div>
      </form>
    </Form>
  )
}

export { SendMessageForm }
