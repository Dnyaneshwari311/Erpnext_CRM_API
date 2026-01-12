import frappe



@frappe.whitelist(allow_guest=False)
def get_language_list():
    languages = frappe.get_all(
        "Language",
        fields=[
            "name",
            "language_name",
            "language_code",
            "enabled"
        ],
        filters={"enabled": 1},
        order_by="language_name"
    )

    return {
        "status": "success",
        "message":"Language List Fetched Successfully",
        "count": len(languages),
        "data": languages
    }




