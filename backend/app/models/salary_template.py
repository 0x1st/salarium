from tortoise import fields
from tortoise.models import Model


class SalaryTemplate(Model):
    """
    Salary template model for storing predefined category templates
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)  # Template name, e.g., "Standard Template", "Executive Template"
    description = fields.CharField(max_length=255, null=True)  # Template description
    
    # Predefined categories stored as JSON
    allowances_template = fields.JSONField(null=True)  # {"交通补贴": 0, "餐补": 0, "通讯补贴": 0}
    bonuses_template = fields.JSONField(null=True)  # {"绩效奖金": 0, "年终奖": 0}
    deductions_template = fields.JSONField(null=True)  # {"迟到扣款": 0, "其他扣除": 0}
    
    # Template metadata
    is_default = fields.BooleanField(default=False)  # Whether this is the default template
    is_active = fields.BooleanField(default=True)  # Whether this template is active
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "salary_templates"
        ordering = ["-created_at"]