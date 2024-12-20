import { Download } from 'lucide-react'

import { Button } from '@/shared/ui'

import type { CommodityResearch as CommodityResearchType } from '../model'

const CommodityResearch = ({
  research,
}: {
  research: CommodityResearchType
}) => {
  return (
    <div className="w-full border p-2 rounded">
      <h3 className="font-bold">
        {research.title ? research.title : 'Нет названия'}
      </h3>
      <div className="flex flex-col gap-2 items-center">
        <p className="mt-2 text-foreground">{research.text}</p>
        <Button variant="ghost" size="sm" asChild>
          <a href={research.url} target="_blank" rel="noreferrer">
            <Download className="h-4 w-4" />
            <span>Скачать</span>
          </a>
        </Button>
      </div>
    </div>
  )
}

export { CommodityResearch }
