import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import * as z from 'zod'

import { useCreateWhitelistMutation } from '@/entities/whitelist'
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

const formSchema = z.object({
  email: z
    .string()
    .email({ message: 'Введите корректную почту' })
    .min(9, { message: 'Почта не может быть такой короткой' })
    .max(255, { message: 'Почта слишком длинная' }),
})

export const CreateWhitelistForm = ({
  onSuccess,
}: {
  onSuccess: () => void
}) => {
  const [create, { isLoading, isError }] = useCreateWhitelistMutation()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    disabled: isLoading,
  })
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      await create(values).unwrap()
      toast.success('Успешно добавлено')
      onSuccess()
    } catch {
      console.log('Не удалось отправить форму')
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {isError && (
          <p className="text-destructive">
            Возникла ошибка. Проверьте корректность указанной почты.
          </p>
        )}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Почтовый адрес</FormLabel>
              <FormControl>
                <Input
                  placeholder="email@sberbank.ru"
                  type="email"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Введите корпоративную почту сотрудника
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Добавляем...' : 'Добавить'}
        </Button>
      </form>
    </Form>
  )
}
