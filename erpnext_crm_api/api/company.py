import frappe



@frappe.whitelist(allow_guest=False)
def get_company_list():
    companies = frappe.get_all(
        "Company",
        fields=[
            "name",
            "company_name",
            "abbr",
            "default_currency",
            "country",
            "is_group",
            "parent_company"
        ],
        order_by="company_name"
    )

    return {
        "status": "success",
        "message":"Company List Fetched Successfully",
        "count": len(companies),
        "data": companies
    }
