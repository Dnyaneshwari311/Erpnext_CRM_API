import frappe

from frappe.utils import cint

@frappe.whitelist()
def list_customers(
    page=1,
    page_size=20,
    search=None,
    order_by="customer_name asc",
    **filters
):
    """
    ERPNext default-style Customer list API
    """

    page = cint(page)
    page_size = cint(page_size)
    start = (page - 1) * page_size

    # Remove internal param
    filters.pop("cmd", None)

    # -----------------------------
    # ERPNext default OR search
    # -----------------------------
    or_filters = []
    if search:
        or_filters = [
            ["Customer", "customer_name", "like", f"%{search}%"],
            ["Customer", "mobile_no", "like", f"%{search}%"],
            ["Customer", "email_id", "like", f"%{search}%"],
        ]

    # -----------------------------
    # Fetch paginated data
    # -----------------------------
    customers = frappe.get_list(
        "Customer",
        fields=[
            "name",
            "customer_name",
            "mobile_no",
            "email_id",
            "disabled"
        ],
        filters=filters,
        or_filters=or_filters,
        order_by=order_by,
        limit_start=start,
        limit_page_length=page_size,
        ignore_permissions=False   # ✅ ERP behavior
    )

    # -----------------------------
    # ERPNext way to get total count
    # -----------------------------
    total_count = len(
        frappe.get_all(
            "Customer",
            filters=filters,
            or_filters=or_filters,
            limit_page_length=0,
            ignore_permissions=False
        )
    )

    return {
        "status": "success",
        "message":"Customer List Fetched Successfully",
        "data": customers,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }