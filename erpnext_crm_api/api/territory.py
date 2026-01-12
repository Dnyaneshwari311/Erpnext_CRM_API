import frappe


@frappe.whitelist(allow_guest=False)
def get_territory_list():
    """
    Returns all territories in ERP hierarchy order
    """

    territories = frappe.get_all(
        "Territory",
        fields=[
            "name",
            "parent_territory",
            "is_group",
            "lft",
            "rgt"
        ],
        order_by="lft"
    )

    return {
        "status": "success",
        "message":"Territory List Fetched Successfully",
        "count": len(territories),
        "data": territories
    }
