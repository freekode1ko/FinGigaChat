import { Check, ChevronsUpDown } from 'lucide-react'
import { useRef, useState } from 'react'
import { type UseFormReturn } from 'react-hook-form'
import { z } from 'zod'

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

import { transformProductsForCombobox } from '../lib'
import { entityFormSchema, type Product } from '../model'

interface ProductFormProps {
  form: UseFormReturn<z.infer<typeof entityFormSchema>>
  onSubmit: (values: z.infer<typeof entityFormSchema>) => void
  actionSlot: React.ReactNode
  products: Array<Product>
}

const ProductForm = ({
  form,
  products,
  onSubmit,
  actionSlot,
}: ProductFormProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [openCombobox, setOpenCombobox] = useState(false)

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 flex flex-col max-w-full">
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
                            'w-full justify-between text-wrap whitespace-normal text-left',
                            !field.value && 'text-muted-foreground'
                          )}
                        >
                          {field.value
                            ? transformProductsForCombobox(products).find(
                                (product) => product.id === field.value
                              )?.name
                            : 'Выбрать продукт...'
                          }
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
                <div>Загружаем продукты...</div>
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
        {actionSlot}
      </form>
    </Form>
  )
}

export { ProductForm }
