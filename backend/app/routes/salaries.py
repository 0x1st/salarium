from typing import List, Optional, Dict, Tuple
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.responses import Response, HTMLResponse
from tortoise.exceptions import IntegrityError
from decimal import Decimal
import io
import pandas as pd

from ..models import (
    SalaryRecord,
    Person,
    SalaryField,
    CustomSalaryValue,
    INCOME_CATEGORIES,
    DEDUCTION_CATEGORIES,
)
from ..schemas.salary import SalaryCreate, SalaryUpdate, SalaryOut
from ..services.payroll import compute_payroll
from ..utils.auth import get_current_user


router = APIRouter()


async def load_custom_fields(
    record_ids: List[int],
) -> Tuple[Dict[int, Dict[str, float]], Dict[int, List[dict]]]:
    """Batch load custom field values for salary records."""
    if not record_ids:
        return {}, {}

    values = await CustomSalaryValue.filter(
        salary_record_id__in=record_ids
    ).prefetch_related("salary_field").all()

    by_record: Dict[int, Dict[str, float]] = {}
    for v in values:
        by_record.setdefault(v.salary_record_id, {})[v.salary_field.field_key] = float(
            v.amount
        )

    payroll_by_record: Dict[int, List[dict]] = {}
    for v in values:
        payroll_by_record.setdefault(v.salary_record_id, []).append(
            {
                "field_type": v.salary_field.field_type,
                "is_non_cash": v.salary_field.is_non_cash,
                "amount": float(v.amount),
            }
        )

    return by_record, payroll_by_record


async def save_custom_fields(
    record_id: int, user_id: int, custom_fields: dict
) -> None:
    """Save custom field values for a salary record."""
    if not custom_fields:
        return

    # Get user's field definitions
    field_defs = await SalaryField.filter(user_id=user_id, is_active=True).all()
    field_map = {f.field_key: f for f in field_defs}

    # Delete existing custom values for this record
    await CustomSalaryValue.filter(salary_record_id=record_id).delete()

    # Create new custom values
    for field_key, amount in custom_fields.items():
        if field_key in field_map and amount != 0:
            await CustomSalaryValue.create(
                salary_record_id=record_id,
                salary_field_id=field_map[field_key].id,
                amount=amount,
            )


def build_salary_out(
    rec: SalaryRecord,
    custom_fields_data: Dict[str, float],
    custom_fields_payroll: List[dict],
) -> SalaryOut:
    data = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        tax=rec.tax,
        custom_fields=custom_fields_payroll or [],
    )
    return SalaryOut(
        id=rec.id,
        year=rec.year,
        month=rec.month,
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        tax=data["tax"],
        total_income=data["total_income"],
        total_deductions=data["total_deductions"],
        gross_income=data["gross_income"],
        net_income=data["net_income"],
        actual_take_home=data["actual_take_home"],
        non_cash_benefits=data["non_cash_benefits"],
        note=rec.note,
        custom_fields=custom_fields_data or {},
    )


def _category_label_map(categories):
    return {k: v for k, v in categories}


def _decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


async def _payslip_context(rec: SalaryRecord, user_id: int):
    values = await CustomSalaryValue.filter(
        salary_record_id=rec.id
    ).prefetch_related("salary_field").all()

    custom_fields = [
        {
            "name": v.salary_field.name,
            "field_type": v.salary_field.field_type,
            "category": v.salary_field.category,
            "amount": float(v.amount),
        }
        for v in values
    ]

    custom_payroll = [
        {
            "field_type": v.salary_field.field_type,
            "is_non_cash": v.salary_field.is_non_cash,
            "amount": float(v.amount),
        }
        for v in values
    ]

    calc = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        tax=rec.tax,
        custom_fields=custom_payroll,
    )

    income_labels = _category_label_map(INCOME_CATEGORIES)
    deduction_labels = _category_label_map(DEDUCTION_CATEGORIES)

    return {
        "year": rec.year,
        "month": rec.month,
        "base_salary": float(rec.base_salary),
        "performance_salary": float(rec.performance_salary),
        "pension_insurance": float(rec.pension_insurance),
        "medical_insurance": float(rec.medical_insurance),
        "unemployment_insurance": float(rec.unemployment_insurance),
        "critical_illness_insurance": float(rec.critical_illness_insurance),
        "enterprise_annuity": float(rec.enterprise_annuity),
        "housing_fund": float(rec.housing_fund),
        "tax": float(rec.tax),
        "note": rec.note or "",
        "custom_fields": custom_fields,
        "calc": calc,
        "income_labels": income_labels,
        "deduction_labels": deduction_labels,
    }


@router.get("/", response_model=List[SalaryOut])
async def list_salaries(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    records = await q.all()
    record_ids = [r.id for r in records]
    custom_data_map, custom_payroll_map = await load_custom_fields(record_ids)
    return [
        build_salary_out(
            r,
            custom_data_map.get(r.id, {}),
            custom_payroll_map.get(r.id, []),
        )
        for r in records
    ]


@router.get("/export")
async def export_salaries(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    format: str = Query(default="csv"),
):
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    records = await q.all()

    record_ids = [r.id for r in records]
    custom_data_map, _ = await load_custom_fields(record_ids)

    fields = await SalaryField.filter(user_id=user.id, is_active=True).all()
    custom_keys = [f.field_key for f in fields]

    rows = []
    for r in records:
        row = {
            "person_id": r.person_id,
            "year": r.year,
            "month": r.month,
            "base_salary": _decimal_to_float(r.base_salary),
            "performance_salary": _decimal_to_float(r.performance_salary),
            "pension_insurance": _decimal_to_float(r.pension_insurance),
            "medical_insurance": _decimal_to_float(r.medical_insurance),
            "unemployment_insurance": _decimal_to_float(r.unemployment_insurance),
            "critical_illness_insurance": _decimal_to_float(
                r.critical_illness_insurance
            ),
            "enterprise_annuity": _decimal_to_float(r.enterprise_annuity),
            "housing_fund": _decimal_to_float(r.housing_fund),
            "tax": _decimal_to_float(r.tax),
            "note": r.note or "",
        }
        custom_fields = custom_data_map.get(r.id, {})
        for key in custom_keys:
            row[key] = custom_fields.get(key, 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    if format == "xlsx":
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        return Response(
            buf.read(),
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            headers={"Content-Disposition": "attachment; filename=salaries.xlsx"},
        )

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=salaries.csv"},
    )


@router.post("/import")
async def import_salaries(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    mode: str = Query(default="upsert"),  # upsert | skip | error
):
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        df = pd.read_csv(file.file)

    fields = await SalaryField.filter(user_id=user.id, is_active=True).all()
    custom_keys = {f.field_key for f in fields}

    required_cols = {"year", "month"}
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少字段: {missing}")

    created = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        row_person_id = int(row.get("person_id") or person_id or 0)
        if not row_person_id:
            raise HTTPException(status_code=400, detail="缺少 person_id")

        person = await Person.filter(id=row_person_id, user_id=user.id).first()
        if not person:
            raise HTTPException(status_code=404, detail=f"人员不存在: {row_person_id}")

        year = int(row.get("year"))
        month = int(row.get("month"))

        existing = await SalaryRecord.filter(
            person_id=row_person_id, year=year, month=month
        ).first()

        if existing and mode == "skip":
            skipped += 1
            continue
        if existing and mode == "error":
            raise HTTPException(
                status_code=400,
                detail=f"记录已存在: person_id={row_person_id} {year}-{month}",
            )

        data = {
            "base_salary": float(row.get("base_salary") or 0),
            "performance_salary": float(row.get("performance_salary") or 0),
            "pension_insurance": float(row.get("pension_insurance") or 0),
            "medical_insurance": float(row.get("medical_insurance") or 0),
            "unemployment_insurance": float(row.get("unemployment_insurance") or 0),
            "critical_illness_insurance": float(
                row.get("critical_illness_insurance") or 0
            ),
            "enterprise_annuity": float(row.get("enterprise_annuity") or 0),
            "housing_fund": float(row.get("housing_fund") or 0),
            "tax": float(row.get("tax") or 0),
            "note": row.get("note") if "note" in df.columns else None,
        }

        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            await existing.save()
            rec = existing
            updated += 1
        else:
            rec = await SalaryRecord.create(
                person_id=row_person_id,
                year=year,
                month=month,
                **data,
            )
            created += 1

        custom_fields = {}
        for key in custom_keys:
            if key in df.columns:
                custom_fields[key] = float(row.get(key) or 0)
        await save_custom_fields(rec.id, user.id, custom_fields)

    return {"created": created, "updated": updated, "skipped": skipped}


@router.post("/{person_id}", response_model=SalaryOut)
async def create_salary(
    person_id: int, payload: SalaryCreate, user=Depends(get_current_user)
):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    try:
        rec = await SalaryRecord.create(
            person_id=person_id,
            year=payload.year,
            month=payload.month,
            base_salary=payload.base_salary,
            performance_salary=payload.performance_salary,
            pension_insurance=payload.pension_insurance,
            medical_insurance=payload.medical_insurance,
            unemployment_insurance=payload.unemployment_insurance,
            critical_illness_insurance=payload.critical_illness_insurance,
            enterprise_annuity=payload.enterprise_annuity,
            housing_fund=payload.housing_fund,
            tax=payload.tax,
            note=payload.note,
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="该月份工资记录已存在")

    # Save custom fields
    if payload.custom_fields:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.get("/{record_id}", response_model=SalaryOut)
async def get_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.get("/{record_id}/payslip.svg")
async def payslip_svg(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    ctx = await _payslip_context(rec, user.id)

    title = f"{ctx['year']}年{ctx['month']}月 工资条"
    net = ctx["calc"]["actual_take_home"]
    insurance_total = (
        ctx["pension_insurance"]
        + ctx["medical_insurance"]
        + ctx["unemployment_insurance"]
        + ctx["critical_illness_insurance"]
        + ctx["enterprise_annuity"]
        + ctx["housing_fund"]
    )
    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="420"',
        ' viewBox="0 0 720 420">',
        '  <rect x="20" y="20" width="680" height="380" rx="16"',
        '    fill="#fffdfb" stroke="#e5e0dc" />',
        '  <text x="40" y="60" font-family="ui-serif, Georgia, serif"',
        f'    font-size="20" fill="#2d2a26">{title}</text>',
        '  <text x="40" y="90" font-family="system-ui, sans-serif"',
        '    font-size="13" fill="#6b6560">实发</text>',
        '  <text x="90" y="90" font-family="system-ui, sans-serif"',
        f'    font-size="16" fill="#2d2a26">¥ {net:.2f}</text>',
        '  <line x1="40" y1="110" x2="680" y2="110" stroke="#eee7e2"/>',
        '  <text x="40" y="140" font-family="system-ui, sans-serif"',
        '    font-size="13" fill="#6b6560">基本工资</text>',
        '  <text x="200" y="140" font-family="system-ui, sans-serif"',
        f'    font-size="13" fill="#2d2a26">¥ {ctx["base_salary"]:.2f}</text>',
        '  <text x="40" y="165" font-family="system-ui, sans-serif"',
        '    font-size="13" fill="#6b6560">绩效工资</text>',
        '  <text x="200" y="165" font-family="system-ui, sans-serif"',
        f'    font-size="13" fill="#2d2a26">¥ {ctx["performance_salary"]:.2f}</text>',
        '  <text x="40" y="200" font-family="system-ui, sans-serif"',
        '    font-size="13" fill="#6b6560">五险一金</text>',
        '  <text x="200" y="200" font-family="system-ui, sans-serif"',
        f'    font-size="13" fill="#2d2a26">¥ {insurance_total:.2f}</text>',
        '  <text x="40" y="225" font-family="system-ui, sans-serif"',
        '    font-size="13" fill="#6b6560">个税</text>',
        '  <text x="200" y="225" font-family="system-ui, sans-serif"',
        f'    font-size="13" fill="#2d2a26">¥ {ctx["tax"]:.2f}</text>',
        '  <text x="40" y="260" font-family="system-ui, sans-serif"',
        f'    font-size="12" fill="#9a9590">备注 {ctx["note"]}</text>',
        "</svg>",
    ]
    svg = "\n".join(svg_lines)
    return Response(svg, media_type="image/svg+xml")


@router.get("/{record_id}/payslip.html")
async def payslip_html(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    ctx = await _payslip_context(rec, user.id)
    title = f"{ctx['year']}年{ctx['month']}月 工资条"
    net = ctx["calc"]["actual_take_home"]
    insurance_total = (
        ctx["pension_insurance"]
        + ctx["medical_insurance"]
        + ctx["unemployment_insurance"]
        + ctx["critical_illness_insurance"]
        + ctx["enterprise_annuity"]
        + ctx["housing_fund"]
    )
    html_lines = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        '  <meta charset="utf-8"/>',
        f"  <title>{title}</title>",
        "  <style>",
        "    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
        "    background:#f6f1ec;color:#2d2a26;padding:24px;}",
        "    .card{max-width:720px;margin:0 auto;background:#fffdfb;",
        "    border:1px solid #e5e0dc;border-radius:16px;padding:24px;}",
        "    h1{font-size:20px;margin:0 0 8px;font-family:ui-serif, Georgia, serif;}",
        "    .net{font-size:18px;margin:8px 0 16px;}",
        "    .row{display:flex;justify-content:space-between;padding:8px 0;",
        "    border-bottom:1px solid #f1ebe7;}",
        "    .muted{color:#6b6560;font-size:13px;}",
        "    .actions{display:flex;gap:8px;margin:16px 0;}",
        "    .btn{padding:6px 10px;border:1px solid #e5e0dc;border-radius:8px;",
        "    background:#f5f3f1;cursor:pointer;}",
        "  </style>",
        "</head>",
        "<body>",
        '  <div class="card">',
        f"    <h1>{title}</h1>",
        f"    <div class=\"net\">实发：¥ {net:.2f}</div>",
        "    <div class=\"row\"><span>基本工资</span>"
        f"<span>¥ {ctx['base_salary']:.2f}</span></div>",
        "    <div class=\"row\"><span>绩效工资</span>"
        f"<span>¥ {ctx['performance_salary']:.2f}</span></div>",
        "    <div class=\"row\"><span>五险一金</span>"
        f"<span>¥ {insurance_total:.2f}</span></div>",
        "    <div class=\"row\"><span>个税</span>"
        f"<span>¥ {ctx['tax']:.2f}</span></div>",
        f"    <div class=\"muted\">备注：{ctx['note']}</div>",
        "    <div class=\"actions\">",
        "      <button class=\"btn\" onclick=\"window.print()\">"
        "打印/保存为PDF</button>",
        (
            "      <a class=\"btn\" id=\"payslip-svg-link\" "
            f"href=\"/api/salaries/{rec.id}/payslip.svg\" download>"
        ),
        "        下载图片(SVG)</a>",
        "    </div>",
        "  </div>",
        "</body>",
        "</html>",
    ]
    html = "\n".join(html_lines)
    return HTMLResponse(html)


@router.put("/{record_id}", response_model=SalaryOut)
async def update_salary(
    record_id: int, payload: SalaryUpdate, user=Depends(get_current_user)
):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Update fixed fields
    update_data = payload.model_dump(exclude_unset=True, exclude={"custom_fields"})
    for field, value in update_data.items():
        setattr(rec, field, value)
    await rec.save()

    # Update custom fields if provided
    if payload.custom_fields is not None:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.delete("/{record_id}")
async def delete_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Delete custom values first (cascade)
    await CustomSalaryValue.filter(salary_record_id=rec.id).delete()

    await rec.delete()
    return {"ok": True}
