import axios from 'axios'
import { useUserStore } from '../store/user'

function client() {
  const user = useUserStore()
  return axios.create({ baseURL: '/api', headers: { Authorization: `Bearer ${user.token}`, 'Cache-Control': 'no-store', Pragma: 'no-cache', Expires: '0' } })
}

function paramsFromFilter({ year, personId, range }) {
  const params = {}
  if (year) params.year = year
  if (personId) params.person_id = personId
  if (range && range.trim()) params.range = range.trim()
  return params
}

export async function fetchPersons() {
  const { data } = await client().get('/persons/')
  return data
}

export async function getYearlyStats(filter) {
  const { data } = await client().get('/stats/yearly', { params: paramsFromFilter(filter) })
  return data
}

export async function getMonthlyStats(filter) {
  const { data } = await client().get('/stats/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getFamilySummary(filter) {
  const { data } = await client().get('/stats/family', { params: paramsFromFilter(filter) })
  return data
}

export async function getMonthlyNetIncome(filter) {
  const { data } = await client().get('/stats/net-income/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getGrossVsNetMonthly(filter) {
  const { data } = await client().get('/stats/gross-vs-net/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getIncomeComposition(filter) {
  const { data } = await client().get('/stats/income-composition', { params: paramsFromFilter(filter) })
  return data
}

export async function getDeductionsBreakdown(filter) {
  const { data } = await client().get('/stats/deductions/breakdown', { params: paramsFromFilter(filter) })
  return data
}

export async function getContributionsCumulative(filter) {
  // contributions requires person_id; ensure it's present
  const params = paramsFromFilter(filter)
  if (!params.person_id) throw new Error('请选择人员以查看累计曲线')
  const { data } = await client().get('/stats/contributions/cumulative', { params })
  return data
}

export async function getMonthlyTable(filter) {
  const { data } = await client().get('/stats/tables/monthly', { params: paramsFromFilter(filter) })
  return data
}

export async function getAnnualTable(filter) {
  const { data } = await client().get('/stats/tables/annual', { params: paramsFromFilter(filter) })
  return data
}
