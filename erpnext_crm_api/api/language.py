# import frappe



# @frappe.whitelist(allow_guest=False)
# def get_language_list():
#     languages = frappe.get_all(
#         "Language",
#         fields=[
#             "name",
#             "language_name",
#             "language_code",
#             "enabled"
#         ],
#         filters={"enabled": 1},
#         order_by="language_name"
#     )

#     return {
#         "status": "success",
#         "message":"Language List Fetched Successfully",
#         "count": len(languages),
#         "data": languages
#     }







import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_language_list(
    search=None,
    sort_by="language_name",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Enabled Language List with Search, Sort & Pagination
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
    allowed_sort_fields = [
        "language_name",
        "language_code",
        "name"
    ]

    if sort_by not in allowed_sort_fields:
        sort_by = "language_name"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    # ---------------------------
    # Filters
    # ---------------------------
    filters = {"enabled": 1}
    or_filters = []

    if search:
        or_filters = [
            ["Language", "language_name", "like", f"%{search}%"],
            ["Language", "language_code", "like", f"%{search}%"],
        ]

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = len(
        frappe.get_all(
            "Language",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # ---------------------------
    # Fetch Records
    # ---------------------------
    languages = frappe.get_all(
        "Language",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "language_name",
            "language_code",
            "enabled"
        ],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # ---------------------------
    # Response
    # ---------------------------
    return {
        "status": "success",
        "message": _("Language List Fetched Successfully"),
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        },
        "data": languages
    }
