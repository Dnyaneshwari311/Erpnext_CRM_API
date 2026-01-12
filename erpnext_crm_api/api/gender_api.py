# import frappe
# @frappe.whitelist(allow_guest=False)
# def get_gender_list():
#     genders = frappe.get_all(
#         "Gender",
#         fields=["name"]
#     )

#     return {
#         "status": "success",
#         "message":"Gender List Fetched Successfully",
#         "count": len(genders),
#         "data": genders
#     }





import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_gender_list(
    search=None,
    sort_by="name",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Gender List with Search, Sort & Pagination
    """

    # ---------------------------
    # Pagination
    # ---------------------------
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # ---------------------------
    # Sorting Validation
    # ---------------------------
    allowed_sort_fields = ["name"]

    if sort_by not in allowed_sort_fields:
        sort_by = "name"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    # ---------------------------
    # Filters
    # ---------------------------
    filters = {}
    or_filters = []

    if search:
        or_filters = [
            ["Gender", "name", "like", f"%{search}%"]
        ]

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = len(
        frappe.get_all(
            "Gender",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # ---------------------------
    # Fetch Records
    # ---------------------------
    genders = frappe.get_all(
        "Gender",
        filters=filters,
        or_filters=or_filters,
        fields=["name"],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # ---------------------------
    # Response
    # ---------------------------
    return {
        "status": "success",
        "message": _("Gender List Fetched Successfully"),
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        },
        "data": genders
    }
