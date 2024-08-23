export const getDefaultDates = () => {
  const now = new Date()
  const nextHour = new Date(now.setHours(now.getHours() + 1, 0, 0, 0))
  const oneHourLater = new Date(nextHour.getTime() + 60 * 60 * 1000)
  const formatToDatetimeLocal = (date: Date) => date.toISOString().slice(0, 16)
  return {
    date_start: formatToDatetimeLocal(nextHour),
    date_end: formatToDatetimeLocal(oneHourLater),
  }
}
