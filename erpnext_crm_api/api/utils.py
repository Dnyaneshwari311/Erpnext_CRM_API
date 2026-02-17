# import frappe

# def api_error(message, status_code=400):
#     frappe.local.response["http_status_code"] = status_code
#     return {
#         "status": "error",
#         "message": message
#     }

# def api_success(data=None, message="Success"):
#     return {
#         "status": "success",
#         "message": message,
#         "data": data
#     }


# import frappe
# from urllib.parse import urlencode
# from frappe import PermissionError


# # ---------------------------------------------------------
# # STANDARD API RESPONSE
# # ---------------------------------------------------------

# def api_response(data=None, message="Success", status_code=200, flatten=False):
#     frappe.local.response["http_status_code"] = status_code

#     response = {
#         "status": "success",
#         "status_code": status_code,
#         "message": message
#     }

#     # 👇 flatten data into root
#     if flatten and isinstance(data, dict):
#         response.update(data)
#     else:
#         response["data"] = data

#     return response

# # ---------------------------------------------------------
# # STANDARD API ERROR (NO TRACEBACK)
# # ---------------------------------------------------------
# def api_error(message, status_code=403):
#     frappe.local.response.clear()

#     frappe.local.response["http_status_code"] = status_code
#     frappe.local.response["message"] = {
#         "status": "error",
#         "message": message
#     }
#     return None


import frappe
import math
from urllib.parse import urlencode
from frappe import PermissionError

# ---------------------------------------------------------
# STANDARD API RESPONSE
# ---------------------------------------------------------
def api_response(data=None, message="Success", status_code=200, flatten=False):
    frappe.local.response["http_status_code"] = status_code

    response = {
        "status": "success",
        "status_code": status_code,
        "message": message
    }

    # 👇 flatten data into root
    if flatten and isinstance(data, dict):
        response.update(data)
    else:
        response["data"] = data

    return response


# ---------------------------------------------------------
# STANDARD API ERROR (NO TRACEBACK)
# ---------------------------------------------------------
def api_error(message, status_code=403):
    frappe.local.response.clear()
    frappe.local.response["http_status_code"] = status_code
    frappe.local.response["message"] = {
        "status": "error",
        "message": str(message)
    }
    return None


# ---------------------------------------------------------
# GENERIC PAGINATED LIST HELPER
# ---------------------------------------------------------
def get_paginated_data(
    doctype,
    fields=None,
    filters=None,
    search=None,
    search_fields=None,
    sort_by="creation",
    sort_order="desc",
    page=1,
    page_size=20,
    is_pagination=True,
    base_url=None,
    extra_params=None,
    or_filters=None
):
    filters = filters or {}
    or_filters = or_filters or []
    extra_params = extra_params or {}

    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -----------------------
    # SEARCH
    # -----------------------
    if search and search_fields:
        search = search.strip()
        for field in search_fields:
            or_filters.append([doctype, field, "like", f"%{search}%"])

    # -----------------------
    # SORT VALIDATION
    # -----------------------
    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    # -----------------------
    # COUNT (FAST)
    # -----------------------
    total_count = len(
        frappe.get_all(
            doctype,
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    # -----------------------
    # DATA FETCH
    # -----------------------
    data = frappe.get_all(
        doctype,
        fields=fields,
        filters=filters,
        or_filters=or_filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    if not is_pagination:
        return data

    total_pages = math.ceil(total_count / page_size) if page_size else 1

    def build_url(p):
        if not base_url:
            return None
        params = {**extra_params, "page": p, "page_size": page_size}
        return f"{base_url}?{urlencode(params)}"

    return {
        "count": total_count,
        "total_pages": total_pages,
        "next": build_url(page + 1) if page < total_pages else None,
        "previous": build_url(page - 1) if page > 1 else None,
        "results": data
    }
