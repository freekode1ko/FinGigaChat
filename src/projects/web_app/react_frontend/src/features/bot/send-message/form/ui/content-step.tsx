import { useFormContext } from "react-hook-form"

import { dropZoneConfig } from "@/entities/bot/model"
import { FileUploadField } from "@/shared/kit"
import { RichTextEditor } from "@/shared/kit/markdown-editor"
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/shared/ui"

export const ContentStep = () => {
  const { control } = useFormContext()

  return (
    <>
      <FormField
          control={control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Текст рассылки</FormLabel>
              <FormControl>
                <RichTextEditor {...field} />
              </FormControl>
              <FormDescription>
                Не вставляйте собственные HTML или Markdown теги, используйте
                этот редактор для форматирования текста
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name="files"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Мультимедиа</FormLabel>
              <FormControl>
                <FileUploadField
                  value={field.value}
                  onValueChange={field.onChange}
                  dropzoneOptions={dropZoneConfig}
                  orientation='horizontal'
                  helpText="Вы можете прикрепить изображения и .PDF документы"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
    </>
  )
}
