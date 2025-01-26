interface Broadcast {
  author_id: number
  message_text: string
  create_at: string
}

interface FullBroadcast extends Broadcast {
  deleted_at: Optional<string>
  broadcast_id: number
}

interface BroadcastWithVersions extends FullBroadcast {
  versions: Array<Broadcast>
}

export type { Broadcast, BroadcastWithVersions, FullBroadcast }
