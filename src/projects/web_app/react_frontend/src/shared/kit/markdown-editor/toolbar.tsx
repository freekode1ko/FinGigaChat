import { Bold, Italic, Strikethrough } from 'lucide-react'

import { Toggle } from '@/shared/ui'
import type { Editor } from '@tiptap/react'

const Toolbar = ({ editor }: { editor: Editor }) => {
  return (
    <div className="border border-border bg-transparent rounded-tr-md rounded-tl-md p-1 flex flex-row items-center gap-1">
      <Toggle
        size="sm"
        pressed={editor.isActive('bold')}
        onPressedChange={() => editor.chain().focus().toggleBold().run()}
      >
        <Bold className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive('italic')}
        onPressedChange={() => editor.chain().focus().toggleItalic().run()}
      >
        <Italic className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive('strike')}
        onPressedChange={() => editor.chain().focus().toggleStrike().run()}
      >
        <Strikethrough className="h-4 w-4" />
      </Toggle>
    </div>
  )
}

export { Toolbar }
