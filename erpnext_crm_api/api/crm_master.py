# import frappe




# from frappe import _

# @frappe.whitelist(allow_guest=True)
# def get_crm_master_list():
#     """
#     API to get all CRM Master entries with key, value, master, and sorting_order
#     """
#     try:
#         data = frappe.get_all(
#             "CRM Master",
#             fields=["master", "key", "value", "sorting_order"],
#             order_by="sorting_order asc"
#         )
#         return {"status": "success", "data": data}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}






import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_crm_master_list(
    search=None,
    sort_by="sorting_order",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get CRM Master List with Search, Sort & Pagination
    Returns fields: master, key, value, sorting_order
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
        allowed_sort_fields = ["master", "key", "value", "sorting_order"]
        if sort_by not in allowed_sort_fields:
            sort_by = "sorting_order"

        sort_order = "desc" if sort_order.lower() == "desc" else "asc"

        # ---------------------------
        # Filters
        # ---------------------------
        filters = {}
        or_filters = []

        if search:
            or_filters = [
                ["CRM Master", "master", "like", f"%{search}%"],
                ["CRM Master", "key", "like", f"%{search}%"],
                ["CRM Master", "value", "like", f"%{search}%"]
            ]

        # ---------------------------
        # Total Count (SAFE)
        # ---------------------------
        total_count = len(
            frappe.get_all(
                "CRM Master",
                filters=filters,
                or_filters=or_filters,
                pluck="name"
            )
        )

        # ---------------------------
        # Fetch Records
        # ---------------------------
        data = frappe.get_all(
            "CRM Master",
            filters=filters,
            or_filters=or_filters,
            fields=["master", "key", "value", "sorting_order"],
            order_by=f"{sort_by} {sort_order}",
            limit_start=start,
            limit_page_length=page_size
        )

        # ---------------------------
        # Response
        # ---------------------------
        return {
            "status": "success",
            "message": _("CRM Master List Fetched Successfully"),
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "data": data
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
