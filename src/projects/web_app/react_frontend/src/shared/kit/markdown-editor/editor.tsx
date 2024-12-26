import { useEffect } from 'react'

import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

import { Toolbar } from './toolbar'

/*
  Компонент для продвинутого редактирования текста, поддерживает HTML.
  Пользователю предоставляется удобный интерфейс для форматирования текста.
*/
const RichTextEditor = ({
  value,
  onChange,
  disabled,
}: {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}) => {
  const editor = useEditor({
    editorProps: {
      attributes: {
        class:
          'min-h-[150px] max-h-[150px] w-full rounded-md rounded-tr-none rounded-tl-none border border-border bg-transparent px-3 py-2 border-t-0 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 overflow-auto',
      },
    },
    extensions: [StarterKit],
    content: value,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
  })

  useEffect(() => {
    if (editor && editor.getHTML() !== value) {
      editor.commands.setContent(value)
    }
  }, [value, editor])

  return (
    <div className="relative max-w-full">
      {editor ? <Toolbar editor={editor} /> : null}
      <EditorContent editor={editor} disabled={disabled} />
    </div>
  )
}

export { RichTextEditor }
