import type { Product } from '../model'

/*
 * Функция преобразует список продуктов, подставляя в их название id.
 * Это необходимо для корректной работы combobox, где требуется уникальность названия.
 */
const transformProductsForCombobox = (products: Array<Product>) => {
  return products.map((product) => ({
    ...product,
    name: `${product.id}. ${product.name}`,
  }))
}

export { transformProductsForCombobox }
