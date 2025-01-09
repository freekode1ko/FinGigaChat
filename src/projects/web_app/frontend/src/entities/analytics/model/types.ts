export interface Menu {
  title: string
  analytics_menu_id: number
  nearest_menu: Array<Menu>
}

export interface Section {
  analytic_id: number
  section: string
  title: string
  text: string
  date: string
}
