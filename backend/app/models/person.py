from tortoise import fields
from tortoise.models import Model


class Person(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    note = fields.CharField(max_length=255, null=True)
    user = fields.ForeignKeyField("models.User", related_name="persons")
    
    # Historical cumulative values (before system tracking)
    pension_history = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    medical_history = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    housing_fund_history = fields.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "persons"