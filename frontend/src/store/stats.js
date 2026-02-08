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
  getMonthlyTable,
  getAnnualTable,
  getAnnualMonthlyTable,
} from '../api/stats'

function cacheKey(name, filter) {
  const parts = [name]
  if (filter.personId) parts.push(`p:${filter.personId}`)
  if (filter.year) parts.push(`y:${filter.year}`)
  if (filter.month) parts.push(`m:${filter.month}`)
  return parts.join('|')
}

export const useStatsStore = defineStore('stats', {
  state: () => ({
    // filters
    personId: null,
    year: new Date().getFullYear(),
    month: null,

    // options
    persons: [],
    loadingPersons: false,
    errorPersons: null,

    // caches
    cache: {},
    inflight: {},

    // ui state
    loading: {},
    errors: {},
    isRefreshing: false,
    _refreshTimer: null,
    _yearCheckedKey: null,

    // invalidation token for cross-view refresh
    refreshToken: 0,
  }),
  getters: {
    filter(state) {
      return { personId: state.personId, year: state.year, month: state.month }
    },
  },
  actions: {
    setPerson(id) {
      this.personId = id ?? null
    },
    setYear(y) {
      this.year = y
    },
    setMonth(m) {
      this.month = m ?? null
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

    async ensureYearWithData() {
      const key = this.personId ? `p:${this.personId}` : 'all'
      if (this._yearCheckedKey === key) return
      this._yearCheckedKey = key
      try {
        const data = await getMonthlyStats({ personId: this.personId })
        if (!data?.length) return
        const latest = Math.max(...data.map(r => r.year).filter(Boolean))
        if (Number.isFinite(latest) && latest !== this.year) {
          this.year = latest
        }
      } catch {
        // ignore; keep current year
      }
    },

    async _useCache(name, fetcher) {
      const key = cacheKey(name, this.filter)
      if (this.cache[key]) return this.cache[key]
      if (this.inflight[key]) return this.inflight[key]
      this.loading[name] = true
      this.errors[name] = null
      const p = (async () => {
        try {
          const data = await fetcher()
          this.cache[key] = data
          return data
        } catch (e) {
          this.errors[name] = e
          throw e
        } finally {
          this.loading[name] = false
          delete this.inflight[key]
        }
      })()
      this.inflight[key] = p
      return p
    },

    // Data loaders
    async loadYearlyStats() {
      return this._useCache('yearly', () => getYearlyStats(this.filter))
    },
    async loadMonthlyStats() {
      return this._useCache('monthly', () => getMonthlyStats(this.filter))
    },
    async loadFamilySummary() {
      return this._useCache('family', () => getFamilySummary(this.filter))
    },
    async loadMonthlyNetIncome() {
      return this._useCache('netMonthly', () => getMonthlyNetIncome(this.filter))
    },
    async loadGrossVsNetMonthly() {
      return this._useCache('grossVsNet', () => getGrossVsNetMonthly(this.filter))
    },
    async loadIncomeComposition() {
      return this._useCache('incomeComposition', () => getIncomeComposition(this.filter))
    },
    async loadDeductionsBreakdown() {
      return this._useCache('deductions', () => getDeductionsBreakdown(this.filter))
    },
    async loadMonthlyTable() {
      return this._useCache('tableMonthly', () => getMonthlyTable(this.filter))
    },
    async loadAnnualTable() {
      return this._useCache('tableAnnual', () => getAnnualTable(this.filter))
    },
    async loadAnnualMonthlyTable() {
      return this._useCache('tableAnnualMonthly', () => getAnnualMonthlyTable(this.filter))
    },

    // helpers
    invalidateCache() {
      this.cache = {}
      this.inflight = {}
      this.loading = {}
      this.errors = {}
      this.refreshToken++
    },
    // alias for clarity
    invalidate() {
      this.invalidateCache()
    },
    async refreshAll() {
      // Debounce refresh to consolidate multiple triggers
      if (this._refreshTimer) clearTimeout(this._refreshTimer)
      this._refreshTimer = setTimeout(async () => {
        this.invalidateCache()
        this.isRefreshing = true
        try {
          const tasks = [
            this.loadMonthlyNetIncome(),
            this.loadGrossVsNetMonthly(),
            this.loadIncomeComposition(),
            this.loadDeductionsBreakdown(),
            this.loadMonthlyTable(),
            this.loadAnnualTable(),
          ]
          await Promise.allSettled(tasks)
        } finally {
          this.isRefreshing = false
        }
      }, 100)
    },
    resetAll() {
      this.personId = null
      this.year = new Date().getFullYear()
      this.month = null
      this.persons = []
      this.loadingPersons = false
      this.errorPersons = null
      this.invalidateCache()
    },
  },
})
