import { useState } from "react"

import { AdaptableModal } from "@/shared/kit"

import { CreateIndustryForm } from "./form"

const CreateIndustryDialog = ({ children }: { children: React.ReactNode }) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title="Добавить отрасль"
      trigger={children}
    >
      <CreateIndustryForm onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { CreateIndustryDialog }
