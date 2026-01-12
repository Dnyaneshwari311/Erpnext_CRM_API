

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_customer_groups():
    """
    Returns list of customer groups with their details.
    """
    groups = frappe.get_all(
        "Customer Group",
        fields=["name", "parent_customer_group", "is_group"]
    )
    
    return {"status": "success", 
            "message":"Customer Group List Fetched Successfully",
            "data": groups}
