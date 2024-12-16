import { EllipsisVertical } from "lucide-react"

import { DeleteIndustryDialog } from "@/features/industries/delete"
import { UpdateIndustryDialog } from "@/features/industries/update"
import { UploadIndustryDocumentDialog } from "@/features/industries/upload-document"
import type { Industry } from "@/entities/industries"
import { Button, DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem,DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/shared/ui"

const ManageIndustryDropdown = ({industry}: {industry: Industry}) => {
  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="ghost">
          <EllipsisVertical className="h-6 w-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Управление отраслью</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <UpdateIndustryDialog industry={industry}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Редактировать
            </DropdownMenuItem>
          </UpdateIndustryDialog>
          <DeleteIndustryDialog industry={industry}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Удалить
            </DropdownMenuItem>
          </DeleteIndustryDialog>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <UploadIndustryDocumentDialog industry={industry}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Документы по отрасли
            </DropdownMenuItem>
          </UploadIndustryDocumentDialog>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { ManageIndustryDropdown }
