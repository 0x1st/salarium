from tortoise import fields
from tortoise.models import Model


class SalaryTemplate(Model):
    """Per-person salary template for auto-fill."""

    id = fields.IntField(pk=True)
    person = fields.ForeignKeyField("models.Person", related_name="salary_templates")

    base_salary = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    performance_salary = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    pension_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    medical_insurance = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    unemployment_insurance = fields.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    critical_illness_insurance = fields.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    enterprise_annuity = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    housing_fund = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    note = fields.CharField(max_length=255, null=True)

    custom_fields = fields.JSONField(null=True)  # {field_key: amount}

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "salary_templates"
        unique_together = ("person_id",)
