# import frappe

# @frappe.whitelist()
# def create_lead_source(data=None):
#     if not data:
#         data = frappe.form_dict

#     if isinstance(data, str):
#         data = frappe.parse_json(data)

#     if not data.get("source_name"):
#         frappe.throw("source_name is required")

#     doc = frappe.new_doc("Lead Source")
#     doc.source_name = data["source_name"]
#     doc.details = data.get("details")
#     doc.insert(ignore_permissions=True)

#     return {
#         "status": "success",
#         "name": doc.name
#     }


import frappe
from erpnext_crm_api.api.utils import api_response, api_error

@frappe.whitelist()
def create_lead_source(data=None):
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    # DO NOT use frappe.throw for API validation
    if not data.get("source_name"):
        frappe.local.response.http_status_code = 400
        return api_error("source_name is required", 400)

    doc = frappe.new_doc("Lead Source")
    doc.source_name = data["source_name"]
    doc.details = data.get("details")
    doc.insert(ignore_permissions=True)

    return api_response(
        data={"name": doc.name},
        message="Lead Source created successfully",
        flatten=True
    )














@frappe.whitelist()
def list_lead_sources(
    page=1,
    page_size=10,
    sort_by="modified",
    sort_order="desc",
    search=None
):
    # Convert to proper types
    page = int(page)
    page_size = int(page_size)

    start = (page - 1) * page_size

    # Build filters
    filters = {}
    if search:
        filters["name"] = ["like", f"%{search}%"]

    data = frappe.get_all(
        "Lead Source",
        fields=["name", "details", "modified"],
        filters=filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    total_count = frappe.db.count("Lead Source", filters=filters)
    return api_response(
        data={
                "page": page,
                "page_size": page_size,
                "total_records": total_count,
                "total_pages": (total_count + page_size - 1),
            "data": data
        },
        message="Lead Sources fetched successfully",
        flatten=True
    )

@frappe.whitelist()
def update_lead_source(name=None, data=None):
    # Fallback to form_dict
    if not name:
        name = frappe.form_dict.get("name")

    if not data:
        data = frappe.form_dict

    # Parse JSON if needed
    if isinstance(data, str):
        data = frappe.parse_json(data)

    if not name:
        return api_error("Lead Source name is required", 400)

    doc = frappe.get_doc("Lead Source", name)

    if "details" in data:
        doc.details = data.get("details")

    doc.save(ignore_permissions=True)

    return api_response(
        data={"name": doc.name},
        message="Lead Source updated successfully",
        flatten=True
    )


@frappe.whitelist()
def delete_lead_source(name=None):
    # fallback to form_dict
    if not name:
        name = frappe.form_dict.get("name")

    if not name:
        return api_error("Lead Source name is required", 400)

    frappe.delete_doc(
        "Lead Source",
        name,
        ignore_permissions=True
    )

    return api_response(
        data={"name": name},
        message="Lead Source deleted successfully",
        flatten=True
    )








@frappe.whitelist()
def get_lead_source(name=None):
    """
    Get a single Lead Source by its name (ID).
    """
    # Fallback to form_dict if name not passed
    if not name:
        name = frappe.form_dict.get("name")

    if not name:
        # frappe.throw("Lead Source name (ID) is required")
        return api_error("Lead Source name (ID) is required", 400)

    # Fetch the doc
    try:
        doc = frappe.get_doc("Lead Source", name)
        return api_response(
            data={
                "name": doc.name,
                "source_name": doc.source_name,
                "details": doc.details,
                "modified": doc.modified
            },
            message="Lead Source fetched successfully",
            flatten=True
        )
    except frappe.DoesNotExistError:
        return api_error(f"Lead Source with name '{name}' does not exist", 403)