import frappe
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error



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
        response_data = {
            "data": groups
        }

        if not full:
            response_data.update({
                "page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            })

        return api_response(
            data=response_data,
            message=_("Customer Group List Fetched Successfully"),
            status_code=200,
            flatten=True
        )


    except Exception as e:
        # return {"status": "error", "message": str(e)}
        return api_error(
            message=str(e), 
            status_code=403
        )

        
