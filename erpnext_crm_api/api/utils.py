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


import frappe
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
        "message": message
    }
    return None


