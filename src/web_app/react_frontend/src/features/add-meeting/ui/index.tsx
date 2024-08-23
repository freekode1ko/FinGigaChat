import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { useCreateMeetingMutation } from '@/entities/meetings'
import { useInitData } from '@/shared/lib'
import {
  Button,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { getDefaultDates } from '../lib'
import { meetingFormSchema } from '../model'

const AddMeetingButton = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [userData] = useInitData()
  const [trigger, { isLoading }] = useCreateMeetingMutation()
  const handleFormSubmit = () => {
    const formValues = meetingForm.getValues()
    trigger({
      user_id: userData?.user?.id || 0,
      ...formValues,
      date_start: new Date(formValues.date_start).toISOString(),
      date_end: new Date(formValues.date_end).toISOString(),
    }).unwrap()
    setIsOpen(false)
  }

  const meetingForm = useForm<z.infer<typeof meetingFormSchema>>({
    resolver: zodResolver(meetingFormSchema),
    defaultValues: {
      ...getDefaultDates(),
      theme: '',
      description: '',
      timezone: 3,
    },
  })
  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="icon">
          <Plus />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>Создать встречу</DrawerTitle>
            <DrawerDescription>
              Вы можете добавить встречу в свой календарь
            </DrawerDescription>
          </DrawerHeader>
          <DrawerFooter>
            <Form {...meetingForm}>
              <form
                onSubmit={meetingForm.handleSubmit(handleFormSubmit)}
                className="space-y-4"
              >
                <FormField
                  control={meetingForm.control}
                  name="theme"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Тема встречи</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Обсуждение текущих задач"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={meetingForm.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Краткое описание</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Встреча с Иваном Ивановым для обсуждения текущих задач"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <div className="flex flex-nowrap gap-2 justify-between">
                  <FormField
                    control={meetingForm.control}
                    name="date_start"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Начало</FormLabel>
                        <FormControl>
                          <Input type="datetime-local" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={meetingForm.control}
                    name="date_end"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Конец</FormLabel>
                        <FormControl>
                          <Input type="datetime-local" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="flex flex-nowrap gap-2">
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? 'Сохраняем...' : 'Сохранить'}
                  </Button>
                  <DrawerClose asChild>
                    <Button variant="outline" className="w-full">
                      Отменить
                    </Button>
                  </DrawerClose>
                </div>
              </form>
            </Form>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { AddMeetingButton }
