export function toNumber(val) {
  const n = Number(val)
  return isNaN(n) ? 0 : n
}

export function formatNumber(val, { decimals = 2, useGrouping = true } = {}) {
  const n = toNumber(val)
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    useGrouping,
  }).format(n)
}

export function formatCurrency(val, { symbol = '¥', decimals = 2 } = {}) {
  return symbol + formatNumber(val, { decimals, useGrouping: true })
}

export function formatPercent(val, { decimals = 1 } = {}) {
  const n = toNumber(val)
  return `${n.toFixed(decimals)}%`
}
