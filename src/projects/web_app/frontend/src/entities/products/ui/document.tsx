import { Download, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/shared/ui'

import type { ProductDocument as ProductDocumentType } from '../model'

const ProductDocument = ({ doc }: { doc: ProductDocumentType }) => {
  const [show, setShow] = useState(false)
  return (
    <div className="w-full border p-2 rounded">
      <h3 className="font-bold">{doc.name}</h3>
      <div className="flex gap-2 items-center">
        {doc.url && (
          <Button variant="ghost" size="sm" asChild>
            <a href={doc.url} target="_blank" rel="noreferrer">
              <Download className="h-4 w-4" />
              <span>Скачать</span>
            </a>
          </Button>
        )}
        {doc.description && (
          <Button variant="ghost" size="sm" onClick={() => setShow(!show)}>
            {show ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
            <span>{show ? 'Скрыть описание' : 'Показать описание'}</span>
          </Button>
        )}
      </div>
      {doc.description && show && (
        <p className="mt-2 text-foreground">{doc.description}</p>
      )}
    </div>
  )
}

export { ProductDocument }
