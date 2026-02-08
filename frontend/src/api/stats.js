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

export async function getYearlyStats(filter) {
  const { data } = await api.get('/stats/yearly', { params: paramsFromFilter(filter) })
  return data
}

export async function getMonthlyStats(filter) {
  const { data } = await api.get('/stats/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getFamilySummary(filter) {
  const { data } = await api.get('/stats/family', { params: paramsFromFilter(filter) })
  return data
}

export async function getMonthlyNetIncome(filter) {
  const { data } = await api.get('/stats/net-income/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getGrossVsNetMonthly(filter) {
  const { data } = await api.get('/stats/gross-vs-net/monthly', { params: paramsFromFilter(filter) })
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

export async function getContributionsCumulative(filter) {
  // contributions requires person_id; ensure it's present
  const params = paramsFromFilter(filter)
  if (!params.person_id) throw new Error('请选择人员以查看累计曲线')
  const { data } = await api.get('/stats/contributions/cumulative', { params })
  return data
}

export async function getMonthlyTable(filter) {
  const { data } = await api.get('/stats/tables/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getAnnualTable(filter) {
  const { data } = await api.get('/stats/tables/annual', { params: paramsFromFilter(filter) })
  return data
}

export async function getAnnualMonthlyTable(filter) {
  const params = paramsFromFilter(filter)
  params.hide_empty = true
  const { data } = await api.get('/stats/tables/annual-monthly', { params })
  return data
}
