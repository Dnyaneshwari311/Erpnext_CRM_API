import frappe



@frappe.whitelist(allow_guest=False)
def get_sales_stage_list():
    """
    Returns all Sales Stages as {id, name, description, probability}
    """

    stages = frappe.get_all(
        "Sales Stage",
        fields=["name"],
        order_by="idx"  # Default order in ERPNext
    )

    data = [
        {
            "id": s["name"],
            "name": s["name"]
        }
        for s in stages
    ]

    return {
        "status": "success",
        "message":"Sales stages List Fetched Successfully",
        "count": len(data),
        "data": data
    }
