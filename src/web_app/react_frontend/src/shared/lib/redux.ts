import { useDispatch, useSelector } from 'react-redux'

export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

export const saveToLocalStorage = (key: string, value: unknown) => {
  const serializedValue = JSON.stringify(value)
  localStorage.setItem(key, serializedValue)
}

export const loadFromLocalStorage = (key: string) => {
  try {
    const serializedValue = localStorage.getItem(key)
    if (serializedValue === null) {
      return undefined
    }
    return JSON.parse(serializedValue)
  } catch (err) {
    console.error(`Ошибка загрузки ${key} из localStorage`, err)
    return undefined
  }
}
