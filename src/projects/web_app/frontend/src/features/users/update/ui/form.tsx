import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import {
  useGetUserRolesQuery,
  type User,
  useUpdateUserRoleMutation,
} from '@/entities/user'
import {
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

const formSchema = z.object({
  role: z.string(),
})

export const UpdateUserRoleForm = ({
  user,
  onSuccess,
}: {
  user: User
  onSuccess?: () => void
}) => {
  const { data: roles } = useGetUserRolesQuery()
  const [update, { isLoading }] = useUpdateUserRoleMutation()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    disabled: isLoading,
    defaultValues: {
      role: user.role.toString(),
    },
  })
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      await update({ roleId: Number(values.role), email: user.email }).unwrap()
      toast.success('Успешно добавлено')
      onSuccess && onSuccess()
    } catch {
      console.log('Не удалось отправить форму')
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Роль пользователя</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {roles?.map((role) => (
                    <SelectItem key={role.id} value={role.id.toString()}>
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Выбранная роль откроет или закроет пользователю доступ к ряду
                функций бота
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Обновляем...' : 'Обновить'}
        </Button>
      </form>
    </Form>
  )
}
