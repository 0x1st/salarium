import api from '../utils/axios'

function paramsFromFilter({ year, month, personId }) {
  const params = {}
  if (year) params.year = year
  if (month) params.month = month
  if (personId) params.person_id = personId
  return params
}

export async function fetchPersons() {
  const { data } = await api.get('/persons/')
  return data
}

export async function getMonthlyStats(filter) {
  const { data } = await api.get('/stats/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getIncomeComposition(filter) {
  const { data } = await api.get('/stats/income-composition', { params: paramsFromFilter(filter) })
  return data
}

export async function getDeductionsBreakdown(filter) {
  const { data } = await api.get('/stats/deductions/breakdown', { params: paramsFromFilter(filter) })
  return data
}
