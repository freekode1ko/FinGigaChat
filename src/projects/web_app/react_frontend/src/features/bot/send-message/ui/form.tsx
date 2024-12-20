import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useSendMessageMutation } from '@/entities/bot'
import {
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Textarea,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

const formSchema = z.object({
  message: z.string().min(1, { message: 'Текст рассылки не может быть пустым' }),
})

const SendMessageForm = () => {
  const [send, { isLoading }] = useSendMessageMutation()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    disabled: isLoading,
    defaultValues: {
      message: '',
    },
  })

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    toast.promise(send(values), {
      loading: 'Отправляем сообщение...',
      success: () => {
        form.reset()
        return 'Сообщение отправлено'
      },
      error: 'Ошибка при отправке сообщения',
    })
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-4"
      >
        <FormField
          control={form.control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Текст рассылки</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Пользователи получат это сообщение в Telegram боте"
                  className="min-h-36"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Вы можете использовать HTML для формирования текста рассылки
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex gap-4 flex-col md:gap-2 md:flex-row-reverse">
          <Button className="w-full md:w-auto" type="submit" disabled={isLoading}>
            Отправить
          </Button>
          <Button className="w-full md:w-auto" type="button" disabled={isLoading} variant="outline" onClick={() => form.reset()}>
            Очистить
          </Button>
        </div>
      </form>
    </Form>
  )
}

export { SendMessageForm }
