import { type UseFormReturn } from 'react-hook-form'
import { z } from 'zod'

import { Combobox } from '@/shared/kit'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
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
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-4 flex flex-col max-w-full"
      >
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
                <Combobox
                  {...field}
                  items={transformProductsForCombobox(products)}
                  placeholder="Корневой продукт"
                />
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
