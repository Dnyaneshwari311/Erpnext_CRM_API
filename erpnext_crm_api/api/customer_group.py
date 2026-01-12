

# import frappe
# from frappe import _

# @frappe.whitelist(allow_guest=True)
# def get_customer_groups():
#     """
#     Returns list of customer groups with their details.
#     """
#     groups = frappe.get_all(
#         "Customer Group",
#         fields=["name", "parent_customer_group", "is_group"]
#     )
    
#     return {"status": "success", 
#             "message":"Customer Group List Fetched Successfully",
#             "data": groups}





import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_customer_groups(
    search=None,
    sort_by="name",
    sort_order="asc",
    page=1,
    page_size=20,
    full=False
):
    """
    API: Get Customer Group List
    Supports search, sort, pagination, and full list
    """

    try:
        # ---------------------------
        # Pagination
        # ---------------------------
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size

        # ---------------------------
        # Sorting Validation
        # ---------------------------
        allowed_sort_fields = ["name", "parent_customer_group", "is_group"]
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
                ["Customer Group", "name", "like", f"%{search}%"],
                ["Customer Group", "parent_customer_group", "like", f"%{search}%"]
            ]

        # ---------------------------
        # Total Count
        # ---------------------------
        total_count = len(
            frappe.get_all(
                "Customer Group",
                filters=filters,
                or_filters=or_filters,
                pluck="name"
            )
        )

        # ---------------------------
        # Fetch Records
        # ---------------------------
        if full:
            # return all records without pagination
            groups = frappe.get_all(
                "Customer Group",
                filters=filters,
                or_filters=or_filters,
                fields=["name", "parent_customer_group", "is_group"],
                order_by=f"{sort_by} {sort_order}"
            )
        else:
            groups = frappe.get_all(
                "Customer Group",
                filters=filters,
                or_filters=or_filters,
                fields=["name", "parent_customer_group", "is_group"],
                order_by=f"{sort_by} {sort_order}",
                limit_start=start,
                limit_page_length=page_size
            )

        # ---------------------------
        # Response
        # ---------------------------
        return {
            "status": "success",
            "message": _("Customer Group List Fetched Successfully"),
            "pagination": None if full else {
                "page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "data": groups
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
