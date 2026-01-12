# import frappe


# @frappe.whitelist(allow_guest=False)
# def get_territory_list():
#     """
#     Returns all territories in ERP hierarchy order
#     """

#     territories = frappe.get_all(
#         "Territory",
#         fields=[
#             "name",
#             "parent_territory",
#             "is_group",
#             "lft",
#             "rgt"
#         ],
#         order_by="lft"
#     )

#     return {
#         "status": "success",
#         "message":"Territory List Fetched Successfully",
#         "count": len(territories),
#         "data": territories
#     }







import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_territory_list(
    search=None,
    sort_by="lft",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Territory List with Search, Sort & Pagination
    Maintains hierarchy order by default
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
        "name",
        "parent_territory",
        "is_group",
        "lft"
    ]

    if sort_by not in allowed_sort_fields:
        sort_by = "lft"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    # ---------------------------
    # Filters
    # ---------------------------
    filters = {}
    or_filters = []

    if search:
        or_filters = [
            ["Territory", "name", "like", f"%{search}%"]
        ]

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = len(
        frappe.get_all(
            "Territory",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # ---------------------------
    # Fetch Records
    # ---------------------------
    territories = frappe.get_all(
        "Territory",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "parent_territory",
            "is_group",
            "lft",
            "rgt"
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
        "message": _("Territory List Fetched Successfully"),
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        },
        "data": territories
    }
