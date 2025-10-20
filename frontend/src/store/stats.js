import { defineStore } from 'pinia'
import {
  fetchPersons,
  getYearlyStats,
  getMonthlyStats,
  getFamilySummary,
  getMonthlyNetIncome,
  getGrossVsNetMonthly,
  getIncomeComposition,
  getDeductionsBreakdown,
  getContributionsCumulative,
  getMonthlyTable,
  getAnnualTable,
} from '../api/stats'

function cacheKey(name, filter) {
  const parts = [name]
  if (filter.personId) parts.push(`p:${filter.personId}`)
  if (filter.year) parts.push(`y:${filter.year}`)
  if (filter.range) parts.push(`r:${filter.range}`)
  return parts.join('|')
}

export const useStatsStore = defineStore('stats', {
  state: () => ({
    // filters
    personId: null,
    year: new Date().getFullYear(),
    range: '',

    // options
    persons: [],
    loadingPersons: false,
    errorPersons: null,

    // caches
    cache: {},

    // ui state
    loading: {},
    errors: {},
  }),
  getters: {
    filter(state) {
      return { personId: state.personId, year: state.year, range: state.range }
    },
  },
  actions: {
    setPerson(id) {
      this.personId = id ?? null
    },
    setYear(y) {
      this.year = y
    },
    setRange(r) {
      this.range = r || ''
    },

    async ensurePersons() {
      if (this.persons.length > 0) return
      this.loadingPersons = true
      this.errorPersons = null
      try {
        this.persons = await fetchPersons()
      } catch (e) {
        this.errorPersons = e
      } finally {
        this.loadingPersons = false
      }
    },

    async _useCache(name, fetcher) {
      const key = cacheKey(name, this.filter)
      if (this.cache[key]) return this.cache[key]
      this.loading[name] = true
      this.errors[name] = null
      try {
        const data = await fetcher()
        this.cache[key] = data
        return data
      } catch (e) {
        this.errors[name] = e
        throw e
      } finally {
        this.loading[name] = false
      }
    },

    // Data loaders
    async loadYearlyStats() {
      return await this._useCache('yearly', () => getYearlyStats(this.filter))
    },
    async loadMonthlyStats() {
      return await this._useCache('monthly', () => getMonthlyStats(this.filter))
    },
    async loadFamilySummary() {
      return await this._useCache('family', () => getFamilySummary(this.filter))
    },
    async loadMonthlyNetIncome() {
      return await this._useCache('netMonthly', () => getMonthlyNetIncome(this.filter))
    },
    async loadGrossVsNetMonthly() {
      return await this._useCache('grossVsNet', () => getGrossVsNetMonthly(this.filter))
    },
    async loadIncomeComposition() {
      return await this._useCache('incomeComposition', () => getIncomeComposition(this.filter))
    },
    async loadDeductionsBreakdown() {
      return await this._useCache('deductions', () => getDeductionsBreakdown(this.filter))
    },
    async loadContributionsCumulative() {
      return await this._useCache('contribCumulative', () => getContributionsCumulative(this.filter))
    },
    async loadMonthlyTable() {
      return await this._useCache('tableMonthly', () => getMonthlyTable(this.filter))
    },
    async loadAnnualTable() {
      return await this._useCache('tableAnnual', () => getAnnualTable(this.filter))
    },

    // helpers
    invalidateCache() {
      this.cache = {}
      this.loading = {}
      this.errors = {}
    },
    resetAll() {
      this.personId = null
      this.year = new Date().getFullYear()
      this.range = ''
      this.persons = []
      this.loadingPersons = false
      this.errorPersons = null
      this.invalidateCache()
    },
  },
})
