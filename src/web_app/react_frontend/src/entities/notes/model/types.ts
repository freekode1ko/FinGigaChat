export interface Note {
  id: string
  user_id: string
  client: string
  report_date: string
  description: string
}

export interface CreateNote extends Pick<Note, 'client' | 'description'> {}
