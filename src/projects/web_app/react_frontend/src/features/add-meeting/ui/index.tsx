import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { useCreateMeetingMutation } from '@/entities/meetings'
import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import {
  Button,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
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

import {
  type AddMeetingFormData,
  getDefaultFormData,
  mapFormData,
  meetingFormSchema,
} from '../model'

/*
 * Кнопка для добавления встречи. При нажатии открывается окно с формой.
 * Закрывается после успешной отправки формы.
 */
const AddMeetingButton = () => {
  const user = useAppSelector(selectUserData)
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [trigger, { isLoading }] = useCreateMeetingMutation()

  const meetingForm = useForm<AddMeetingFormData>({
    resolver: zodResolver(meetingFormSchema),
    defaultValues: getDefaultFormData(),
    disabled: isLoading,
  })
  const onSubmit = async () => {
    await trigger(mapFormData(meetingForm.getValues(), user!.id)).unwrap()
    meetingForm.reset()
    setIsOpen(false)
  }

  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="icon">
          <Plus />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full">
          <DrawerHeader>
            <DrawerTitle>Создать встречу</DrawerTitle>
            <DrawerDescription>
              Вы можете добавить встречу в свой календарь
            </DrawerDescription>
          </DrawerHeader>
          <Form {...meetingForm}>
            <form
              onSubmit={meetingForm.handleSubmit(onSubmit)}
              className="space-y-4 w-full max-h-[400px] overflow-y-auto p-2"
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
              <FormField
                control={meetingForm.control}
                name="timezone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Временная зона</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="3" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex gap-2">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Сохраняем...' : 'Сохранить'}
                </Button>
                <DrawerClose asChild>
                  <Button variant="outline" className="w-full">
                    Закрыть
                  </Button>
                </DrawerClose>
              </div>
            </form>
          </Form>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { AddMeetingButton }
