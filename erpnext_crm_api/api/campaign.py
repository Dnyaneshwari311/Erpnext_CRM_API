import frappe


@frappe.whitelist(allow_guest=False)
def get_campaign_list():
    campaigns = frappe.get_all(
        "Campaign",
        fields=[
            "name",
            "campaign_name",
            "owner"
        ],
        order_by="creation desc"
    )

    return {
        "status": "success",
        "message":"Campaign List Fetched Successfully",
        "count": len(campaigns),
        "data": campaigns
    }
