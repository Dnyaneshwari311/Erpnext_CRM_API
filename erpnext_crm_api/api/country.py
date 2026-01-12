import frappe 


@frappe.whitelist(allow_guest=False)
def get_country_list():
    countries = frappe.get_all(
        "Country",
        fields=[
            "name",
            "code",
            "date_format",
            "time_format",
            "time_zones"
        ],
        order_by="name"
    )

    return {
        "status": "success",
        "message":"Country List Fetched Successfully",
        "count": len(countries),
        "data": countries
    }
