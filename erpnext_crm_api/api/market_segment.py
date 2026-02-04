import frappe
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error


@frappe.whitelist(allow_guest=False)
def get_market_segment_list(
    search=None,
    sort_by="name",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Market Segment List with Search, Sort & Pagination
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
            ["Market Segment", "name", "like", f"%{search}%"]
        ]

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = len(
        frappe.get_all(
            "Market Segment",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # ---------------------------
    # Fetch Records
    # ---------------------------
    segments = frappe.get_all(
        "Market Segment",
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
    return api_response(
    data={
        "page": page,
        "page_size": page_size,
        "total_records": total_count,
        "total_pages": (total_count + page_size - 1) // page_size,
        "data": segments
    },
    message=_("Market Segment List Fetched Successfully"),
    status_code=200,
    flatten=True
)
