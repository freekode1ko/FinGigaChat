import { type UseFormReturn } from "react-hook-form"
import { z } from "zod"

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger,Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage, Input } from "@/shared/ui"

import type { entityFormSchema } from "../model"

interface IndustryFormProps {
  form: UseFormReturn<z.infer<typeof entityFormSchema>>
  onSubmit: (values: z.infer<typeof entityFormSchema>) => void
  actionSlot: React.ReactNode
}

const IndustryForm = ({form, onSubmit, actionSlot}: IndustryFormProps) => {
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Название отрасли</FormLabel>
              <FormControl>
                <Input placeholder="Нефть и газ" {...field} />
              </FormControl>
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

export { IndustryForm }
