export interface ProductDocument {
  id: number
  name: string
  description: string | null
  url: string
}

export interface CreateProductDocument {
  name: string
  description?: string
  file: File
}

export interface ShortProduct {
  id: number
  name: string
  description: string | null
  display_order: number
  name_latin: string | null
  parent_id: number
}

export interface Product extends ShortProduct {
  documents: Array<ProductDocument>
  children: Array<Product>
}

interface CreateProduct {
  name: string
  description?: string | null
  parent_id: number
  display_order: number
  name_latin?: string | null
}

export type { CreateProduct }
