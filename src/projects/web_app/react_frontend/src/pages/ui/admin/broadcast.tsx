import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { useGetFullMessageQuery } from "@/entities/bot"
import { BroadcastVersionCard } from "@/entities/bot/ui/broadcast-version"
import { AdaptableModal } from "@/shared/kit"
import { ADMIN_MAP } from "@/shared/model"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Skeleton } from "@/shared/ui"

const AdminBroadcastPage = () => {
  const navigate = useNavigate()
  const { broadcastId } = useParams() as { broadcastId: string }
  const { data: broadcast, isLoading, isError } = useGetFullMessageQuery({broadcastId: parseInt(broadcastId)})
  const [selectedVersion, setSelectedVersion] = useState<string>('')

  if (!broadcast) return (
    <AdaptableModal title='История рассылки' open onOpenChange={() => navigate(ADMIN_MAP.bot)}>
      {isError && <p className="mt-2 text-center text-muted-foreground">Такая рассылка не найдена</p>}
      {isLoading && (
        <div className="flex flex-col gap-2">
          <Skeleton className="w-full h-10" />
          <Skeleton className="w-full h-64" />
        </div>
      )}
    </AdaptableModal>
  )

  if (selectedVersion === '' && broadcast.message.versions.length > 0) {
    setSelectedVersion(broadcast.message.versions[0].create_at)
  }

  const currentVersion = broadcast.message.versions.find(
    (v) => v.create_at === selectedVersion
  )

  return (
    <AdaptableModal title={`История рассылки #${broadcastId}`} open onOpenChange={() => navigate(ADMIN_MAP.bot)}>
      <div className="flex flex-col gap-2">
        <Select onValueChange={setSelectedVersion} value={selectedVersion}>
          <SelectTrigger>
            <SelectValue placeholder="Выберите версию" />
          </SelectTrigger>
          <SelectContent>
            {broadcast.message.versions.map(version => (
              <SelectItem key={version.create_at} value={version.create_at}>
                {new Date(version.create_at).toLocaleString(undefined, {year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric'})}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {currentVersion &&
          <div className="hidden md:block max-h-[460px] overflow-y-auto">
            <BroadcastVersionCard
              broadcast={currentVersion}
              isNewest={selectedVersion === broadcast.message.versions[0].create_at}
            />
          </div>
        }
      </div>
    </AdaptableModal>
  )
}

export { AdminBroadcastPage }
