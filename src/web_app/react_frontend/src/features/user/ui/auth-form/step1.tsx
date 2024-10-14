import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  Button,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { loginFormSchema } from '../../model'

export const AuthFormStep1 = ({
  onSuccessNavigate,
}: {
  onSuccessNavigate: () => void
}) => {
  const isLoading = false
  const trigger = (values: z.infer<typeof loginFormSchema>) => {
    console.log(values)
    /*
    1. Отправить запрос
    2. Дождаться ответ
    3. Если 2хх - вызвать navigate на подтверждение кодом
    */
    onSuccessNavigate()
  }

  const form = useForm<z.infer<typeof loginFormSchema>>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { email: '' },
    disabled: isLoading,
  })

  return (
    <Form {...form}>
      <form
        className="pt-4 space-y-4 w-full lg:space-y-8 lg:pt-8"
        onSubmit={form.handleSubmit((values) => trigger(values))}
      >
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Почтовый адрес</FormLabel>
              <FormControl>
                <Input placeholder="me@sberbank.ru" {...field} type="email" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isLoading} className="w-full">
          {isLoading ? 'Проверяем данные...' : 'Продолжить'}
        </Button>
      </form>
    </Form>
  )
}
