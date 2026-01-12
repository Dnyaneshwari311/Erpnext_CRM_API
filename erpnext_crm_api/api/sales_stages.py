# import frappe



# @frappe.whitelist(allow_guest=False)
# def get_sales_stage_list():
#     """
#     Returns all Sales Stages as {id, name, description, probability}
#     """

#     stages = frappe.get_all(
#         "Sales Stage",
#         fields=["name"],
#         order_by="idx"  # Default order in ERPNext
#     )

#     data = [
#         {
#             "id": s["name"],
#             "name": s["name"]
#         }
#         for s in stages
#     ]

#     return {
#         "status": "success",
#         "message":"Sales stages List Fetched Successfully",
#         "count": len(data),
#         "data": data
#     }




import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_sales_stage_list(
    search=None,
    sort_by="idx",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Sales Stage List with Search, Sort & Pagination
    Preserves ERPNext default ordering using idx
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
    allowed_sort_fields = ["idx", "name"]

    if sort_by not in allowed_sort_fields:
        sort_by = "idx"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    # ---------------------------
    # Filters
    # ---------------------------
    filters = {}
    or_filters = []

    if search:
        or_filters = [
            ["Sales Stage", "name", "like", f"%{search}%"]
        ]

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = len(
        frappe.get_all(
            "Sales Stage",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # ---------------------------
    # Fetch Records
    # ---------------------------
    stages = frappe.get_all(
        "Sales Stage",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "idx"],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # ---------------------------
    # Format Response Data
    # ---------------------------
    data = [
        {
            "id": s["name"],
            "name": s["name"]
        }
        for s in stages
    ]

    # ---------------------------
    # Response
    # ---------------------------
    return {
        "status": "success",
        "message": _("Sales Stages List Fetched Successfully"),
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        },
        "data": data
    }
