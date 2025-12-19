import frappe

def api_error(message, status_code=400):
    frappe.local.response["http_status_code"] = status_code
    return {
        "status": "error",
        "message": message
    }

def api_success(data=None, message="Success"):
    return {
        "status": "success",
        "message": message,
        "data": data
    }
