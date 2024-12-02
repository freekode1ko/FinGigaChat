import { Check, ChevronsUpDown } from 'lucide-react'
import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import * as z from 'zod'

import {
  type Product,
  useCreateProductMutation,
  useGetProductsQuery,
  useUpdateProductMutation,
} from '@/entities/products'
import { cn } from '@/shared/lib'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
  Button,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Textarea,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

/*
 * Функция преобразует список продуктов, подставляя в их название id.
 * Это необходимо для корректной работы combobox, где требуется уникальность названия.
 */
const transformProductsForCombobox = (products: Array<Product>) => {
  return products.map((product) => ({
    ...product,
    name: `${product.id}. ${product.name}`,
  }))
}

const formSchema = z.object({
  name: z.string().min(1, { message: 'Название не может отсутствовать' }),
  description: z.string().optional(),
  parent_id: z.number().default(0),
  name_latin: z.string().optional(),
  display_order: z.coerce
    .number({
      invalid_type_error: 'Порядок должен быть целым числом',
    })
    .int()
    .positive()
    .min(1, { message: 'Порядок не может быть меньше 1' }),
})

export const CreateProductForm = ({
  item,
  onSuccess,
}: {
  item?: Product | null
  onSuccess?: () => void
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [openCombobox, setOpenCombobox] = useState(false)
  const { data: products } = useGetProductsQuery()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: item?.name || '',
      description: item?.description || '',
      display_order: item?.display_order || 1,
      name_latin: item?.name_latin || '',
      parent_id: item?.parent_id ?? 0,
    },
  })

  const [create] = useCreateProductMutation()
  const [update] = useUpdateProductMutation()

  function onSubmit(values: z.infer<typeof formSchema>) {
    if (item) {
      toast.promise(update({ product: values, id: item.id }).unwrap(), {
        loading: `Обновляем ${item.name}...`,
        success: 'Изменения сохранены!',
        error: 'Мы не смогли сохранить изменения. Попробуйте позже.',
      })
    } else {
      toast.promise(create(values).unwrap(), {
        loading: 'Создаем продукт...',
        success: 'Продукт успешно создан!',
        error: 'Мы не смогли сохранить продукт. Попробуйте позже.',
      })
    }
    onSuccess && onSuccess()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Название продукта</FormLabel>
              <FormControl>
                <Input placeholder="Hot Offers" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Описание продукта</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Очень классный продукт!"
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="parent_id"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Родительский продукт</FormLabel>
              {products ? (
                <div ref={containerRef}>
                  <Popover open={openCombobox} onOpenChange={setOpenCombobox}>
                    <PopoverTrigger asChild>
                      <FormControl>
                        <Button
                          variant="outline"
                          role="combobox"
                          className={cn(
                            'w-full justify-between',
                            !field.value && 'text-muted-foreground'
                          )}
                        >
                          {field.value
                            ? transformProductsForCombobox(products).find(
                                (product) => product.id === field.value
                              )?.name
                            : 'Выбрать продукт...'}
                          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </FormControl>
                    </PopoverTrigger>
                    <PopoverContent
                      className="min-w-full p-0"
                      container={containerRef.current}
                    >
                      <Command>
                        <CommandInput placeholder="Поиск по продуктам..." />
                        <CommandList>
                          <CommandEmpty>Таких продуктов нет</CommandEmpty>
                          <CommandGroup>
                            {transformProductsForCombobox(products).map(
                              (product) => (
                                <CommandItem
                                  value={product.name}
                                  key={product.id}
                                  onSelect={() => {
                                    form.setValue('parent_id', product.id)
                                    setOpenCombobox(false)
                                  }}
                                >
                                  <Check
                                    className={cn(
                                      'mr-2 h-4 w-4',
                                      product.id === field.value
                                        ? 'opacity-100'
                                        : 'opacity-0'
                                    )}
                                  />
                                  {product.name}
                                </CommandItem>
                              )
                            )}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
                </div>
              ) : (
                <div>loading...</div>
              )}
              <FormDescription>
                Вы можете выбрать родительский продукт
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <Accordion type="single" collapsible>
          <AccordionItem value="advanced-settings">
            <AccordionTrigger>Продвинутые настройки</AccordionTrigger>
            <AccordionContent className="space-y-4 p-2">
              <FormField
                control={form.control}
                name="name_latin"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Латинское название</FormLabel>
                    <FormControl>
                      <Input placeholder="hot_offers" type="" {...field} />
                    </FormControl>
                    <FormDescription>
                      Вы можете ввести латинское название данного продукта
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="display_order"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Порядок отображения</FormLabel>
                    <FormControl>
                      <Input placeholder="1" type="number" {...field} />
                    </FormControl>
                    <FormDescription>
                      Заполняйте это поле только в том случае, если знаете, что
                      делаете
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
        <Button type="submit" className="w-full">
          {item ? 'Обновить' : 'Создать'}
        </Button>
      </form>
    </Form>
  )
}
