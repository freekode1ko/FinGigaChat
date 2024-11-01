import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { useLoginMutation } from '@/entities/user'
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

import { loginFormSchema } from '../../model'

export const EmailStep = ({
  onEmailChange,
  onSuccessNavigate,
}: {
  onEmailChange: (email: string) => void
  onSuccessNavigate: () => void
}) => {
  const [login, {isLoading}] = useLoginMutation()
  const trigger = async (values: z.infer<typeof loginFormSchema>) => {
    onEmailChange(values.email)
    try {
      await login(values).unwrap()
      toast.success('Мы отправили вам на почту код для входа в систему')
      onSuccessNavigate()
    } catch {
      toast.error('Проверьте корректность введенной почты и попробуйте еще раз')
    }
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
              <FormDescription>Если вы входите впервые, то сначала вам необходимо зарегистрироваться в боте</FormDescription>
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
