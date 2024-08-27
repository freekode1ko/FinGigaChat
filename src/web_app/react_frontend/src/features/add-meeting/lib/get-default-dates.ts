export const getDefaultDates = () => {
  const now = new Date()
  const nextHour = new Date(now)
  nextHour.setHours(now.getHours() + 1, 0, 0, 0)
  const oneHourLater = new Date(nextHour.getTime() + 60 * 60 * 1000)
  const formatToDatetimeLocal = (date: Date) => {
    const tzoffset = date.getTimezoneOffset() * 60000
    return new Date(date.getTime() - tzoffset).toISOString().slice(0, 16)
  }
  return [formatToDatetimeLocal(nextHour), formatToDatetimeLocal(oneHourLater)]
}
