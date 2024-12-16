import { Download } from "lucide-react"

import { Button } from "@/shared/ui"

import type { IndustryDocument as IndustryDocumentType } from "../model"
  
const IndustryDocument = ({ doc }: { doc: IndustryDocumentType }) => {
  return (
    <div className="w-full border p-2 rounded">
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
