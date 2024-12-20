interface WhitelistUser {
  email: string
}

interface CreateWhitelistUser extends WhitelistUser {}
interface DeleteWhitelistUser extends WhitelistUser {}

export type { CreateWhitelistUser, DeleteWhitelistUser, WhitelistUser }
