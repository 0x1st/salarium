# Backend Tests

## Running Tests

To run all tests:
```bash
cd /home/engine/project/backend
PYTHONPATH=/home/engine/project/backend python -m pytest tests/ -v
```

To run specific test file:
```bash
cd /home/engine/project/backend
PYTHONPATH=/home/engine/project/backend python -m pytest tests/test_gross_to_net_calculation.py -v
```

## Test Coverage

### `test_gross_to_net_calculation.py`
Tests for the waterfall chart gross-to-net calculation, ensuring that:
- Meal allowances are excluded from gross income
- Festival benefits (Mid-Autumn, Dragon Boat, Spring Festival) are excluded from gross income
- Other income is included in gross income
- Net income = Gross income - Deductions
- Monthly and annual aggregations work correctly

## Dependencies

Tests require:
- pytest
- pytest-asyncio
- httpx

Install with:
```bash
uv pip install pytest pytest-asyncio httpx
```
