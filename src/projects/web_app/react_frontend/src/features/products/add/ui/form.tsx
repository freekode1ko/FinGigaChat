import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  entityFormSchema,
  ProductForm,
  useCreateProductMutation,
  useGetProductsQuery,
} from '@/entities/products'
import { Button } from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

export const CreateProductForm = ({
  onSuccess,
}: {
  onSuccess?: () => void
}) => {
  const { data: products } = useGetProductsQuery()
  const [create, { isLoading }] = useCreateProductMutation()

  const form = useForm<z.infer<typeof entityFormSchema>>({
    resolver: zodResolver(entityFormSchema),
    disabled: isLoading,
    defaultValues: {
      name: '',
      description: '',
      display_order: 1,
      name_latin: '',
      parent_id: 0,
    },
  })

  const handleSubmit = (values: z.infer<typeof entityFormSchema>) => {
    create(values).unwrap()
    onSuccess && onSuccess()
  }

  return (
    <ProductForm
      form={form}
      products={products || []}
      onSubmit={handleSubmit}
      actionSlot={
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Создаем...' : 'Создать'}
        </Button>
      }
    />
  )
}
