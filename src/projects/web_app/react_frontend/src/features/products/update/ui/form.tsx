import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  entityFormSchema,
  type Product,
  ProductForm,
  useGetProductsQuery,
  useUpdateProductMutation,
} from '@/entities/products'
import { Button } from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

export const UpdateProductForm = ({
  product,
  onSuccess,
}: {
  product: Product
  onSuccess?: () => void
}) => {
  const { data: products } = useGetProductsQuery()
  const [update, { isLoading }] = useUpdateProductMutation()

  const form = useForm<z.infer<typeof entityFormSchema>>({
    resolver: zodResolver(entityFormSchema),
    disabled: isLoading,
    defaultValues: {
      name: product.name,
      description: product.description || '',
      display_order: product.display_order,
      name_latin: product.name_latin || '',
      parent_id: product.parent_id,
    },
  })

  const handleSubmit = async (values: z.infer<typeof entityFormSchema>) => {
    await update({ product: values, id: product.id }).unwrap()
    onSuccess && onSuccess()
  }

  return (
    <ProductForm
      form={form}
      products={products || []}
      onSubmit={handleSubmit}
      actionSlot={
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Обновляем...' : 'Обновить'}
        </Button>
      }
    />
  )
}
