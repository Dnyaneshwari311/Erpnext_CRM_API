import frappe


@frappe.whitelist(allow_guest=False)
def get_opportunity_type_list():
    """
    Returns Opportunity Type master records as {id, name, description}
    """

    types = frappe.get_all(
        "Opportunity Type",  # This is the DocType name in your screenshot
        fields=["name", "description"],
        order_by="name"
    )

    # Map name → id, for dropdown-friendly API
    data = [{"id": t["name"], "name": t["name"], "description": t.get("description", "")} for t in types]

    return {
        "status": "success",
        "message":"Opportunity Type List Fetched Successfully",
        "count": len(data),
        "data": data
    }
