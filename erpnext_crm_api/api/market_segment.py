import frappe

@frappe.whitelist(allow_guest=False)
def get_market_segment_list():
    segments = frappe.get_all(
        "Market Segment",
        fields=["name"],
        order_by="name"
    )

    return {
        "status": "success",
        "message":"Market Segment List Fetched Successfully",
        "count": len(segments),
        "data": segments
    }
