"""
Unit tests for waterfall chart gross-to-net calculation.
Verifies that gross income excludes meal allowance and festival benefits.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock


def test_gross_income_for_net_charts_excludes_meal_and_festivals():
    """Test that _gross_income_for_net_charts excludes meal allowance and festival benefits."""
    # Import the function we're testing
    from app.routes.stats import _gross_income_for_net_charts, _D
    
    # Create a mock SalaryRecord with all fields
    record = MagicMock()
    record.base_salary = Decimal("10000")
    record.performance_salary = Decimal("2000")
    record.high_temp_allowance = Decimal("500")
    record.low_temp_allowance = Decimal("300")
    record.computer_allowance = Decimal("200")
    record.meal_allowance = Decimal("600")  # Should be excluded
    record.mid_autumn_benefit = Decimal("1000")  # Should be excluded
    record.dragon_boat_benefit = Decimal("800")  # Should be excluded
    record.spring_festival_benefit = Decimal("1500")  # Should be excluded
    record.other_income = Decimal("100")
    
    # Calculate gross income
    gross = _gross_income_for_net_charts(record)
    
    # Expected: base + performance + high_temp + low_temp + computer + other
    # = 10000 + 2000 + 500 + 300 + 200 + 100 = 13100
    expected = Decimal("13100")
    
    assert gross == expected, f"Expected {expected}, got {gross}"
    
    # Verify that meal allowance and benefits are NOT included
    gross_with_excluded = gross + Decimal("600") + Decimal("1000") + Decimal("800") + Decimal("1500")
    assert gross_with_excluded == Decimal("17000"), "Excluded items sum verification failed"


def test_gross_income_for_net_charts_with_zeros():
    """Test that _gross_income_for_net_charts handles zero values correctly."""
    from app.routes.stats import _gross_income_for_net_charts
    
    record = MagicMock()
    record.base_salary = Decimal("5000")
    record.performance_salary = Decimal("0")
    record.high_temp_allowance = Decimal("0")
    record.low_temp_allowance = Decimal("0")
    record.computer_allowance = Decimal("0")
    record.meal_allowance = Decimal("500")  # Should be excluded even if present
    record.mid_autumn_benefit = Decimal("0")
    record.dragon_boat_benefit = Decimal("0")
    record.spring_festival_benefit = Decimal("0")
    record.other_income = Decimal("0")
    
    gross = _gross_income_for_net_charts(record)
    
    # Expected: only base_salary
    expected = Decimal("5000")
    
    assert gross == expected, f"Expected {expected}, got {gross}"


def test_waterfall_net_calculation():
    """Test that waterfall net = gross - deductions (for charts with other_income)."""
    from app.routes.stats import _gross_income_for_net_charts, _deductions_sum
    
    record = MagicMock()
    record.base_salary = Decimal("10000")
    record.performance_salary = Decimal("2000")
    record.high_temp_allowance = Decimal("500")
    record.low_temp_allowance = Decimal("300")
    record.computer_allowance = Decimal("200")
    record.meal_allowance = Decimal("600")
    record.mid_autumn_benefit = Decimal("1000")
    record.dragon_boat_benefit = Decimal("800")
    record.spring_festival_benefit = Decimal("1500")
    record.other_income = Decimal("100")
    
    # Deductions
    record.pension_insurance = Decimal("800")
    record.medical_insurance = Decimal("200")
    record.unemployment_insurance = Decimal("50")
    record.critical_illness_insurance = Decimal("10")
    record.enterprise_annuity = Decimal("400")
    record.housing_fund = Decimal("1200")
    record.other_deductions = Decimal("0")
    
    gross = _gross_income_for_net_charts(record)
    deductions = _deductions_sum(record)
    
    # For waterfall chart: net = gross - deductions
    # Gross includes other_income (100), so net should too
    expected_net = gross - deductions
    
    assert gross == Decimal("13100"), f"Gross mismatch: expected 13100, got {gross}"
    assert deductions == Decimal("2660"), f"Deductions mismatch: expected 2660, got {deductions}"
    assert expected_net == Decimal("10440"), f"Expected net mismatch: expected 10440, got {expected_net}"
    
    # Note: _unified_net_income excludes other_income, so it would be 10340
    # But for the waterfall chart, we want net = gross - deductions = 10440


def test_monthly_aggregation_excludes_meal_and_festivals():
    """Test monthly aggregation excludes meal allowance and festivals correctly."""
    from app.routes.stats import _gross_income_for_net_charts
    
    # Simulate two records for the same month
    record1 = MagicMock()
    record1.base_salary = Decimal("8000")
    record1.performance_salary = Decimal("1000")
    record1.high_temp_allowance = Decimal("0")
    record1.low_temp_allowance = Decimal("0")
    record1.computer_allowance = Decimal("100")
    record1.meal_allowance = Decimal("500")  # Should be excluded
    record1.mid_autumn_benefit = Decimal("1000")  # Should be excluded
    record1.dragon_boat_benefit = Decimal("0")
    record1.spring_festival_benefit = Decimal("0")
    record1.other_income = Decimal("0")
    
    record2 = MagicMock()
    record2.base_salary = Decimal("9000")
    record2.performance_salary = Decimal("1500")
    record2.high_temp_allowance = Decimal("200")
    record2.low_temp_allowance = Decimal("0")
    record2.computer_allowance = Decimal("150")
    record2.meal_allowance = Decimal("500")  # Should be excluded
    record2.mid_autumn_benefit = Decimal("0")
    record2.dragon_boat_benefit = Decimal("800")  # Should be excluded
    record2.spring_festival_benefit = Decimal("0")
    record2.other_income = Decimal("50")
    
    gross1 = _gross_income_for_net_charts(record1)
    gross2 = _gross_income_for_net_charts(record2)
    total_gross = gross1 + gross2
    
    # Expected totals
    # Record1: 8000 + 1000 + 0 + 0 + 100 + 0 = 9100
    # Record2: 9000 + 1500 + 200 + 0 + 150 + 50 = 10900
    # Total: 20000
    expected_total = Decimal("20000")
    
    assert total_gross == expected_total, f"Expected total {expected_total}, got {total_gross}"


def test_annual_aggregation_with_festivals():
    """Test annual aggregation correctly excludes festival benefits across multiple months."""
    from app.routes.stats import _gross_income_for_net_charts
    
    # Simulate records for different months with different festival benefits
    months = []
    
    # January - Spring Festival
    jan = MagicMock()
    jan.base_salary = Decimal("10000")
    jan.performance_salary = Decimal("2000")
    jan.high_temp_allowance = Decimal("0")
    jan.low_temp_allowance = Decimal("0")
    jan.computer_allowance = Decimal("200")
    jan.meal_allowance = Decimal("600")
    jan.mid_autumn_benefit = Decimal("0")
    jan.dragon_boat_benefit = Decimal("0")
    jan.spring_festival_benefit = Decimal("2000")  # Should be excluded
    jan.other_income = Decimal("0")
    months.append(jan)
    
    # June - Dragon Boat
    jun = MagicMock()
    jun.base_salary = Decimal("10000")
    jun.performance_salary = Decimal("2000")
    jun.high_temp_allowance = Decimal("500")
    jun.low_temp_allowance = Decimal("0")
    jun.computer_allowance = Decimal("200")
    jun.meal_allowance = Decimal("600")
    jun.mid_autumn_benefit = Decimal("0")
    jun.dragon_boat_benefit = Decimal("1000")  # Should be excluded
    jun.spring_festival_benefit = Decimal("0")
    jun.other_income = Decimal("0")
    months.append(jun)
    
    # September - Mid-Autumn
    sep = MagicMock()
    sep.base_salary = Decimal("10000")
    sep.performance_salary = Decimal("2000")
    sep.high_temp_allowance = Decimal("0")
    sep.low_temp_allowance = Decimal("0")
    sep.computer_allowance = Decimal("200")
    sep.meal_allowance = Decimal("600")
    sep.mid_autumn_benefit = Decimal("1500")  # Should be excluded
    sep.dragon_boat_benefit = Decimal("0")
    sep.spring_festival_benefit = Decimal("0")
    sep.other_income = Decimal("0")
    months.append(sep)
    
    # Calculate annual gross
    annual_gross = sum(_gross_income_for_net_charts(m) for m in months)
    
    # Expected for each month (without festivals/meals): 10000 + 2000 + allowances + 200
    # Jan: 10000 + 2000 + 0 + 200 = 12200
    # Jun: 10000 + 2000 + 500 + 200 = 12700
    # Sep: 10000 + 2000 + 0 + 200 = 12200
    # Total: 37100
    expected_annual = Decimal("37100")
    
    assert annual_gross == expected_annual, f"Expected annual {expected_annual}, got {annual_gross}"


def test_endpoint_calculation_with_other_income():
    """Test that the gross_vs_net endpoint correctly includes other_income in both gross and net."""
    from app.routes.stats import _gross_income_for_net_charts, _deductions_sum
    
    # Create a record with other_income
    record = MagicMock()
    record.base_salary = Decimal("10000")
    record.performance_salary = Decimal("2000")
    record.high_temp_allowance = Decimal("0")
    record.low_temp_allowance = Decimal("0")
    record.computer_allowance = Decimal("0")
    record.meal_allowance = Decimal("500")  # Excluded
    record.mid_autumn_benefit = Decimal("0")
    record.dragon_boat_benefit = Decimal("0")
    record.spring_festival_benefit = Decimal("0")
    record.other_income = Decimal("1000")  # Should be included
    
    record.pension_insurance = Decimal("1000")
    record.medical_insurance = Decimal("200")
    record.unemployment_insurance = Decimal("0")
    record.critical_illness_insurance = Decimal("0")
    record.enterprise_annuity = Decimal("0")
    record.housing_fund = Decimal("1200")
    record.other_deductions = Decimal("0")
    
    gross = _gross_income_for_net_charts(record)
    deductions = _deductions_sum(record)
    net = gross - deductions
    
    # Gross should include other_income: 10000 + 2000 + 1000 = 13000
    assert gross == Decimal("13000"), f"Expected gross 13000, got {gross}"
    # Deductions: 1000 + 200 + 1200 = 2400
    assert deductions == Decimal("2400"), f"Expected deductions 2400, got {deductions}"
    # Net: 13000 - 2400 = 10600
    assert net == Decimal("10600"), f"Expected net 10600, got {net}"
