from tortoise import fields
from tortoise.models import Model


class SalaryRecord(Model):
    id = fields.IntField(pk=True)
    person = fields.ForeignKeyField("models.Person", related_name="salary_records")
    year = fields.IntField()
    month = fields.IntField()  # 1-12

    base_salary = fields.FloatField(default=0.0)
    performance_percent = fields.FloatField(null=True)  # e.g., 0.1 for 10%
    performance_fixed = fields.FloatField(null=True)

    allowances = fields.JSONField(null=True)  # {"交通": 100, "餐补": 200}
    bonuses = fields.JSONField(null=True)  # {"年终奖": 5000}
    deductions = fields.JSONField(null=True)  # {"迟到扣款": 50, "其他扣除": 100}

    ins_pension = fields.FloatField(default=0.0)
    ins_medical = fields.FloatField(default=0.0)
    ins_unemployment = fields.FloatField(default=0.0)
    ins_injury = fields.FloatField(default=0.0)
    ins_maternity = fields.FloatField(default=0.0)
    housing_fund = fields.FloatField(default=0.0)

    tax = fields.FloatField(default=0.0)  # 个人所得税（自动或手动）

    note = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "salary_records"
        unique_together = ("person_id", "year", "month")