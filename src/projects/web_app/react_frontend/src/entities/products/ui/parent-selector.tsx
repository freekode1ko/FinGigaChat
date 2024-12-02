import { type ShortProduct } from '../model'

interface ParentSelectorProps {
  options: Array<ShortProduct>
}

/*
 * Компонент для выбора родительского продукта из списка.
 * На вход принимает список продуктов, по которым осуществляет поиск.
 */
export const ParentSelector = ({ options }: ParentSelectorProps) => {
  return (
    <div>
      {options.map((option) => (
        <li key={option.id} value={option.id}>
          {option.name}
        </li>
      ))}
    </div>
  )
}
