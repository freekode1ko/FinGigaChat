import { useForm } from 'react-hook-form'

import { type Note, useUpdateNoteMutation } from '@/entities/notes'
import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import {
  Button,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  Input,
  Textarea,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import {
  CreateNoteFormData,
  getDefaultFormData,
  mapUpdateFormData,
  noteFormSchema,
} from '../model'

const UpdateNoteForm = ({
  note,
  onEdited,
}: {
  note: Note
  onEdited: () => void
}) => {
  const user = useAppSelector(selectUserData)
  const [trigger, { isLoading }] = useUpdateNoteMutation()
  const updateNoteForm = useForm<CreateNoteFormData>({
    resolver: zodResolver(noteFormSchema),
    defaultValues: getDefaultFormData(note.client, note.description),
    disabled: isLoading,
  })
  const onSubmit = async () => {
    await trigger(
      mapUpdateFormData(updateNoteForm.getValues(), user!.id, note.id)
    ).unwrap()
    updateNoteForm.reset()
    onEdited()
  }

  return (
    <Form {...updateNoteForm}>
      <form
        onSubmit={updateNoteForm.handleSubmit(onSubmit)}
        className="space-y-4 w-full max-h-[400px] overflow-y-auto p-2"
      >
        <FormField
          control={updateNoteForm.control}
          name="client"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input
                  variant="ghost"
                  fieldSize="lg"
                  placeholder="Введите название заметки..."
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={updateNoteForm.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Textarea
                  variant="ghost"
                  placeholder="Введите текст заметки..."
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex gap-2">
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Сохраняем...' : 'Сохранить'}
          </Button>
          <Button variant="outline" className="w-full" onClick={onEdited}>
            Отменить
          </Button>
        </div>
      </form>
    </Form>
  )
}

export { UpdateNoteForm }
