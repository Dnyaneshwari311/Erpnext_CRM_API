import frappe
@frappe.whitelist(allow_guest=False)
def get_gender_list():
    genders = frappe.get_all(
        "Gender",
        fields=["name"]
    )

    return {
        "status": "success",
        "message":"Gender List Fetched Successfully",
        "count": len(genders),
        "data": genders
    }
