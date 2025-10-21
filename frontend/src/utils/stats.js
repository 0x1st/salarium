// Utilities for statistics modules
// hasStatsData: determine whether the dataset contains any meaningful (non-zero) numeric values.
// Rules:
// - If all numeric series sum to 0 or data arrays are empty, return false
// - Ignore structural numeric fields like year/month/person_id/percent
export function hasStatsData(input) {
  if (!input) return false
  const ignoreKeys = new Set(['year', 'month', 'person_id', 'personId', 'percent'])

  const isFiniteNumber = (v) => typeof v === 'number' && Number.isFinite(v)

  function sumObject(obj) {
    let s = 0
    for (const [k, v] of Object.entries(obj || {})) {
      if (ignoreKeys.has(k)) continue
      if (k === 'summary' && Array.isArray(v)) {
        // Special: [{ category, amount, percent }]
        s += v.reduce((acc, it) => acc + (isFiniteNumber(it?.amount) ? it.amount : 0), 0)
        continue
      }
      if (k === 'monthly' && Array.isArray(v)) {
        for (const m of v) {
          for (const [mk, mv] of Object.entries(m || {})) {
            if (ignoreKeys.has(mk)) continue
            s += isFiniteNumber(mv) ? mv : 0
          }
        }
        continue
      }
      s += sumAny(v)
    }
    return s
  }

  function sumArray(arr) {
    let s = 0
    for (const item of arr) {
      s += sumAny(item)
    }
    return s
  }

  function sumAny(v) {
    if (v == null) return 0
    if (isFiniteNumber(v)) return v
    if (Array.isArray(v)) return sumArray(v)
    if (typeof v === 'object') return sumObject(v)
    return 0
  }

  const total = sumAny(input)
  return total > 0
}
