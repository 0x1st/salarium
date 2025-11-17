from tortoise import fields
from tortoise.models import Model


class SalaryRecord(Model):
    id = fields.IntField(pk=True)
    person = fields.ForeignKeyField("models.Person", related_name="salary_records")
    year = fields.IntField()
    month = fields.IntField()  # 1-12

    # Fixed income fields
    base_salary = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    performance_salary = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    high_temp_allowance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    low_temp_allowance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    computer_allowance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    communication_allowance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    meal_allowance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    mid_autumn_benefit = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    dragon_boat_benefit = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    spring_festival_benefit = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_income = fields.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Fixed deduction fields
    pension_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    medical_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    unemployment_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    critical_illness_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    enterprise_annuity = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    housing_fund = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deductions = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    labor_union_fee = fields.DecimalField(max_digits=15, decimal_places=2, default=0)

    tax = fields.DecimalField(max_digits=15, decimal_places=2, default=0)

    note = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "salary_records"
        unique_together = ("person_id", "year", "month")
