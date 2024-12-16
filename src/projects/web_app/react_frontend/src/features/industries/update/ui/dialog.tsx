import { useState } from "react"

import { type Industry } from "@/entities/industries"
import { AdaptableModal } from "@/shared/kit"

import { UpdateIndustryForm } from "./form"

const UpdateIndustryDialog = ({industry, children}: {industry: Industry, children: React.ReactNode}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Редактировать ${industry.name}`}
      trigger={children}
    >
      <UpdateIndustryForm industry={industry} onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { UpdateIndustryDialog }
