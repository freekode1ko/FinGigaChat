import { Download } from 'lucide-react'

import { Button } from '@/shared/ui'

import type { IndustryDocument as IndustryDocumentType } from '../model'

const IndustryDocument = ({ doc, actionSlot }: { doc: IndustryDocumentType, actionSlot?: React.ReactNode }) => {
  return (
    <div className="w-full border p-2 rounded">
      {actionSlot && <div className="absolute top-0 right-0">{actionSlot}</div>}
      <h3 className="font-bold">{doc.name}</h3>
      <div className="flex gap-2 industrys-center">
        <Button variant="ghost" size="sm" asChild>
          <a href={doc.url} target="_blank" rel="noreferrer">
            <Download className="h-4 w-4" />
            <span>Скачать</span>
          </a>
        </Button>
      </div>
    </div>
  )
}

export { IndustryDocument }
