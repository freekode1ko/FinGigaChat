import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  entityFormSchema,
  IndustryForm,
  useCreateIndustryMutation,
} from '@/entities/industries'
import { Button } from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

export const CreateIndustryForm = ({
  onSuccess,
}: {
  onSuccess?: () => void
}) => {
  const [create, { isLoading }] = useCreateIndustryMutation()

  const form = useForm<z.infer<typeof entityFormSchema>>({
    resolver: zodResolver(entityFormSchema),
    disabled: isLoading,
    defaultValues: {
      name: '',
      display_order: 1,
    },
  })

  const handleSubmit = (values: z.infer<typeof entityFormSchema>) => {
    create(values).unwrap()
    onSuccess && onSuccess()
  }

  return (
    <IndustryForm
      form={form}
      onSubmit={handleSubmit}
      actionSlot={
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Создаем...' : 'Создать'}
        </Button>
      }
    />
  )
}
