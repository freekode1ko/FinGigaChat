import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { confirmationFormSchema } from '../../model'

export const AuthFormStep2 = ({
  onSuccessNavigate,
}: {
  onSuccessNavigate: () => void
}) => {
  const isLoading = false
  const trigger = (values: z.infer<typeof confirmationFormSchema>) => {
    console.log(values)
    /*
    1. Отправить запрос
    2. Дождаться ответ
    3. Если 2хх - вызвать navigate на дашборд
    */
    onSuccessNavigate()
  }

  const form = useForm<z.infer<typeof confirmationFormSchema>>({
    resolver: zodResolver(confirmationFormSchema),
    defaultValues: { code: '' },
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
          name="code"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Одноразовый пароль</FormLabel>
              <FormControl>
                <InputOTP maxLength={6} {...field}>
                  <InputOTPGroup>
                    {Array.from({ length: 6 }).map((_, index) => (
                      <InputOTPSlot key={index} index={index} />
                    ))}
                  </InputOTPGroup>
                </InputOTP>
              </FormControl>
              <FormDescription>
                Пожалуйста, введите одноразовый пароль, который вы получили на
                указанную почту.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isLoading} className="w-full">
          {isLoading ? 'Проверяем данные...' : 'Подтвердить'}
        </Button>
      </form>
    </Form>
  )
}
