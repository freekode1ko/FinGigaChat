import { Settings } from "lucide-react"
import { Link } from "react-router-dom"

import { selectUserData } from "@/entities/auth"
import { useAppSelector } from "@/shared/lib"
import { ADMIN_MAP } from "@/shared/model"
import { Button } from "@/shared/ui"

/*
  Кнопка для быстрого доступа в панель управления. Доступна только для администраторов.
*/
const AdminButton = () => {
  const user = useAppSelector(selectUserData)

  if (user?.role !== 1) return null
  return (
    <div className='fixed top-1/2 right-[-3px] -translate-y-1/2 border-l border-t border-b border-border p-2 bg-secondary z-50'>
      <Button size='icon' variant='ghost' className='h-10 w-10 animate-spin-slow' asChild>
        <Link to={ADMIN_MAP.home}>
          <Settings />
        </Link>
      </Button>
    </div>
  )
}

export {AdminButton}
