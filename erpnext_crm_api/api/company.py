# import frappe



# @frappe.whitelist(allow_guest=False)
# def get_company_list():
#     companies = frappe.get_all(
#         "Company",
#         fields=[
#             "name",
#             "company_name",
#             "abbr",
#             "default_currency",
#             "country",
#             "is_group",
#             "parent_company"
#         ],
#         order_by="company_name"
#     )

#     return {
#         "status": "success",
#         "message":"Company List Fetched Successfully",
#         "count": len(companies),
#         "data": companies
#     }



import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_company_list(
    search=None,
    sort_by="company_name",
    sort_order="asc",
    page=1,
    page_size=20
):
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    allowed_sort_fields = [
        "company_name",
        "abbr",
        "country",
        "default_currency",
        "name"
    ]

    if sort_by not in allowed_sort_fields:
        sort_by = "company_name"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    filters = {}
    or_filters = []

    # ✅ OR search
    if search:
        or_filters = [
            ["Company", "company_name", "like", f"%{search}%"],
            ["Company", "abbr", "like", f"%{search}%"],
            ["Company", "country", "like", f"%{search}%"],
        ]

    # ✅ Total count (CORRECT WAY)
    total_count = len(
        frappe.get_all(
            "Company",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    companies = frappe.get_all(
        "Company",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "company_name",
            "abbr",
            "default_currency",
            "country",
            "is_group",
            "parent_company"
        ],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    return {
        "status": "success",
        "message": _("Company List Fetched Successfully"),
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        },
        "data": companies
    }
