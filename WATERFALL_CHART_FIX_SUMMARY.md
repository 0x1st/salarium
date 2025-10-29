# Waterfall Chart Gross-to-Net Calculation Fix

## Summary
Fixed the waterfall chart calculation to exclude meal allowances and festival benefits from the gross amount, ensuring consistency with the homepage net amount display.

## Changes Made

### Backend Changes

#### 1. New Helper Function (`/backend/app/routes/stats.py`)
Added `_gross_income_for_net_charts()` function:
```python
def _gross_income_for_net_charts(r: SalaryRecord) -> Decimal:
    """Gross income for waterfall and gross-vs-net charts:
    Excludes meal allowance and festival benefits per unified spec.
    应发 = 基本工资 + 绩效工资 + 高温补贴 + 低温补贴 + 电脑补贴 + 其他（排除：餐补、三节福利）
    """
    return (
        _D(r.base_salary)
        + _D(r.performance_salary)
        + _allowances_sum_net(r)  # excludes meal allowance
        + _D(r.other_income)
    )
```

**What it excludes:**
- Meal allowance (餐补)
- Mid-Autumn benefit (中秋福利)
- Dragon Boat benefit (端午福利)
- Spring Festival benefit (春节福利)

**What it includes:**
- Base salary (基本工资)
- Performance salary (绩效工资)
- High temperature allowance (高温补贴)
- Low temperature allowance (低温补贴)
- Computer allowance (电脑补贴)
- Other income (其他)

#### 2. Updated Endpoint (`/backend/app/routes/stats.py`)
Modified `/stats/gross-vs-net/monthly` endpoint to:
- Use `_gross_income_for_net_charts()` for gross calculation
- Calculate net as `gross - deductions` (instead of using `_unified_net_income`)
- This ensures net includes `other_income` when gross does

#### 3. Unit Tests (`/backend/tests/test_gross_to_net_calculation.py`)
Created comprehensive unit tests covering:
- Basic exclusion of meal allowance and festival benefits
- Handling of zero values
- Waterfall net calculation (gross - deductions)
- Monthly aggregation
- Annual aggregation with multiple festival months
- Other income inclusion in both gross and net

### Frontend Changes

#### 1. WaterfallChart Component (`/frontend/src/components/stats/WaterfallChart.vue`)
- Added default note: "应发不包含餐补与三节福利"
- Enhanced tooltip to show full description: "应发工资（不含餐补与福利）"

#### 2. GrossVsNetBar Component (`/frontend/src/components/stats/GrossVsNetBar.vue`)
- Added default note: "应发不包含餐补与三节福利" for consistency

## Calculation Formula

### Before Fix
- **Gross**: base + performance + high_temp + low_temp + meal + computer + festivals + other
- **Net**: _unified_net_income (excludes meal, festivals, AND other_income)

### After Fix
- **Gross**: base + performance + high_temp + low_temp + computer + other (excludes meal & festivals)
- **Deductions**: pension + medical + unemployment + critical_illness + annuity + housing_fund + other_deductions
- **Net**: Gross - Deductions (now includes other_income)

## Testing

All 6 unit tests pass successfully:
1. ✅ `test_gross_income_for_net_charts_excludes_meal_and_festivals`
2. ✅ `test_gross_income_for_net_charts_with_zeros`
3. ✅ `test_waterfall_net_calculation`
4. ✅ `test_monthly_aggregation_excludes_meal_and_festivals`
5. ✅ `test_annual_aggregation_with_festivals`
6. ✅ `test_endpoint_calculation_with_other_income`

## Impact

### Affected Components
- Waterfall Chart (应发 → 扣除 → 实际到手)
- Gross vs Net Bar Chart (应发 vs 实际到手)
- KPI Cards on Net Income page (showing gross, deductions, and net totals)

### Not Affected
- Other endpoints that use `_unified_net_income` remain unchanged
- Detail tables and other statistics views maintain their existing calculations

## Verification Steps

To verify the fix:
1. Select a month containing meal allowances and festival benefits
2. Check that the waterfall chart's "应发" amount equals:
   - Sum of: base_salary + performance_salary + allowances (excluding meal) + other_income
   - Excluding: meal_allowance + mid_autumn_benefit + dragon_boat_benefit + spring_festival_benefit
3. Verify "实际到手" = "应发" - "扣除"
4. Confirm consistency between waterfall chart and bar chart displays

## Acceptance Criteria Met

✅ Waterfall chart's "应发" excludes meal allowances and three festival benefits
✅ Calculation is consistent with other related charts/tables
✅ Backend unit tests pass
✅ Frontend renders correctly with clarifying notes
✅ Tooltips and legends clearly indicate the exclusions
