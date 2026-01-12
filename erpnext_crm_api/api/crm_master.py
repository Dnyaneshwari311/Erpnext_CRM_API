import frappe




from frappe import _

@frappe.whitelist(allow_guest=True)
def get_crm_master_list():
    """
    API to get all CRM Master entries with key, value, master, and sorting_order
    """
    try:
        data = frappe.get_all(
            "CRM Master",
            fields=["master", "key", "value", "sorting_order"],
            order_by="sorting_order asc"
        )
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
