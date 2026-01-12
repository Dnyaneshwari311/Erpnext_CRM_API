import frappe


@frappe.whitelist(allow_guest=False)
def get_industry_list():
    industries = frappe.get_all(
        "Industry Type",
        fields=["name"],
        order_by="name"
    )

    return {
        "status": "success",
        "message":"Industry List Fetched Successfully",
        "count": len(industries),
        "data": industries
    }
