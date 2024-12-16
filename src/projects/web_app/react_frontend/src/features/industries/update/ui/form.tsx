import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  entityFormSchema,
  type Industry,
  IndustryForm,
  useUpdateIndustryMutation,
} from '@/entities/industries'
import {
  Button,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

export const UpdateIndustryForm = ({ industry, onSuccess }: {industry: Industry, onSuccess?: () => void}) => {
  const [update, { isLoading }] = useUpdateIndustryMutation()

  const form = useForm<z.infer<typeof entityFormSchema>>({
    resolver: zodResolver(entityFormSchema),
    disabled: isLoading,
    defaultValues: {...industry},
  })

  const handleSubmit = async (values: z.infer<typeof entityFormSchema>) => {
    await update({industry: values, id: industry.id}).unwrap()
    onSuccess && onSuccess()
  }

  return (
    <IndustryForm
      form={form}
      onSubmit={handleSubmit}
      actionSlot={
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Обновляем...' : 'Обновить'}
        </Button>
      }
    />
  )
}
