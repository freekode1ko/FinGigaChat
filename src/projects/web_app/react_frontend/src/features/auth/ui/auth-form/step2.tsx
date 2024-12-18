import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  setUser,
  useLazyGetCurrentUserQuery,
  useVerifyCodeMutation,
} from '@/entities/auth'
import { useAppDispatch } from '@/shared/lib'
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

export const ConfirmationCodeStep = ({
  forEmail,
  onSuccessNavigate,
}: {
  forEmail: string
  onSuccessNavigate: () => void
}) => {
  const dispatch = useAppDispatch()
  const [getUser, { isLoading: userLoading }] = useLazyGetCurrentUserQuery()
  const [verifyCode, { isLoading }] = useVerifyCodeMutation()
  const trigger = async (values: z.infer<typeof confirmationFormSchema>) => {
    try {
      await verifyCode({ ...values, email: forEmail }).unwrap()
      const user = await getUser().unwrap()
      dispatch(setUser(user))
      onSuccessNavigate()
    } catch {
      toast.error(`Некорректный код`)
    }
  }

  const form = useForm<z.infer<typeof confirmationFormSchema>>({
    resolver: zodResolver(confirmationFormSchema),
    defaultValues: { reg_code: '' },
    disabled: isLoading || userLoading,
  })

  return (
    <Form {...form}>
      <form
        className="pt-4 space-y-4 w-full lg:space-y-8 lg:pt-8"
        onSubmit={form.handleSubmit((values) => trigger(values))}
      >
        <FormField
          control={form.control}
          name="reg_code"
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
                Пожалуйста, введите одноразовый пароль, который вы получили по
                почте.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          disabled={isLoading || userLoading}
          className="w-full"
        >
          {isLoading || userLoading ? 'Проверяем данные...' : 'Подтвердить'}
        </Button>
      </form>
    </Form>
  )
}
