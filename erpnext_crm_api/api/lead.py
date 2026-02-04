import frappe
import json
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error


@frappe.whitelist()
def create_lead(data=None):
    # Fallback to form_dict
    if not data:
        data = frappe.form_dict

    # Parse JSON string if required
    if isinstance(data, str):
        data = frappe.parse_json(data)

    # Mandatory validation
    if not data.get("first_name"):
        api_error("first_name is required", 400)

    if not data.get("status"):
        api_error("status is required", 400)

    lead = frappe.new_doc("Lead")

    # ---- Basic Info ----
    lead.salutation = data.get("salutation")
    lead.first_name = data.get("first_name")
    lead.middle_name = data.get("middle_name")
    lead.last_name = data.get("last_name")
    lead.gender = data.get("gender")
    lead.status = data.get("status")
    lead.source = data.get("source")
    lead.type = data.get("type")
    lead.request_type = data.get("request_type")

    # ---- Contact Info ----
    lead.email_id = data.get("email")
    lead.mobile_no = data.get("mobile_no")
    lead.phone = data.get("phone")
    lead.whatsapp_no = data.get("whatsapp")
    lead.website = data.get("website")
    lead.phone_ext = data.get("phone_ext")

    # ---- Company Info ----
    lead.company_name = data.get("organization_name")
    lead.annual_revenue = data.get("annual_revenue")
    lead.no_of_employees = data.get("no_of_employees")
    lead.industry = data.get("industry")
    lead.market_segment = data.get("market_segment")

    # ---- Address ----
    lead.city = data.get("city")
    lead.state = data.get("state")
    lead.country = data.get("country")
    lead.territory = data.get("territory")

    # ---- Qualification ----
    lead.qualification_status = data.get("qualification_status")
    lead.qualified_by = data.get("qualified_by")
    lead.qualified_on = data.get("qualified_on")

    # ---- Marketing ----
    lead.campaign_name = data.get("campaign_name")
    lead.company = data.get("company")
    lead.print_language = data.get("print_language")

    # ---- Flags ----
    lead.disabled = data.get("disabled", 0)
    lead.unsubscribed = data.get("unsubscribed", 0)
    lead.blog_subscriber = data.get("blog_subscriber", 0)

    lead.insert(ignore_permissions=True)

    return api_response(
        data={"lead_id": lead.name},
        message="Lead created successfully",
        status_code=201
    )









# @frappe.whitelist()
# def list_leads(
#     page=1,
#     page_size=10,
#     sort_by="modified",
#     sort_order="desc",
#     search=None,
#     status=None,
#     source=None
# ):
#     page = int(page)
#     page_size = int(page_size)
#     start = (page - 1) * page_size

#     # AND filters
#     filters = {}
#     if status:
#         filters["status"] = status
#     if source:
#         filters["source"] = source

#     # OR filters (search)
#     or_filters = []
#     if search:
#         or_filters = [
#             ["Lead", "first_name", "like", f"%{search}%"],
#             ["Lead", "last_name", "like", f"%{search}%"],
#             ["Lead", "email_id", "like", f"%{search}%"],
#             ["Lead", "mobile_no", "like", f"%{search}%"],
#             ["Lead", "company_name", "like", f"%{search}%"],
#         ]

#     # ---- DATA QUERY ----
#     leads = frappe.get_all(
#         "Lead",
#         fields=[
#             "name",
#             "first_name",
#             "last_name",
#             "status",
#             "source",
#             "email_id",
#             "mobile_no",
#             "company_name",
#             "modified"
#         ],
#         filters=filters,
#         or_filters=or_filters,
#         order_by=f"{sort_by} {sort_order}",
#         limit_start=start,
#         limit_page_length=page_size
#     )

#     # ---- TOTAL COUNT (supports or_filters) ----
#     total_count = len(
#         frappe.get_all(
#             "Lead",
#             filters=filters,
#             or_filters=or_filters,
#             pluck="name"
#         )
#     )

#     total_pages = (total_count + page_size - 1) // page_size

#     return {
#         "status": "success",

#         # pagination info
#         "page": page,
#         "page_size": page_size,
#         "total": total_count,
#         "total_pages": total_pages,

#         # navigation helpers
        
#         "next_page": page + 1 if page < total_pages else None,
#         "prev_page": page - 1 if page > 1 else None,

#         # actual data
#         "data": leads
#     }


@frappe.whitelist()
def list_leads(
    page=1,
    page_size=10,
    sort_by="modified",
    sort_order="desc",
    search=None,
    status=None,
    source=None
):
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -------------------
    # AND Filters
    # -------------------
    filters = {}
    if status:
        filters["status"] = status
    if source:
        filters["source"] = source

    # -------------------
    # OR Filters (Search)
    # -------------------
    or_filters = []
    if search:
        or_filters = [
            ["Lead", "first_name", "like", f"%{search}%"],
            ["Lead", "last_name", "like", f"%{search}%"],
            ["Lead", "email_id", "like", f"%{search}%"],
            ["Lead", "mobile_no", "like", f"%{search}%"],
            ["Lead", "company_name", "like", f"%{search}%"],
        ]

    # -------------------
    # DATA QUERY (ALL FIELDS)
    # -------------------
    leads = frappe.get_all(
        "Lead",
        fields=["*"],
        filters=filters,
        or_filters=or_filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # -------------------
    # TOTAL COUNT (FIXED)
    # -------------------
    total_count = len(
        frappe.get_all(
            "Lead",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    total_pages = (total_count + page_size - 1) // page_size
    return api_response(
    data={
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,
        "data": leads
    },
    message="Leads fetched successfully",
    status_code=200,
    flatten=True
)





@frappe.whitelist()
def update_lead():
    """
    Update Lead API
    """

    # ✅ SAFE JSON PARSING
    try:
        data = json.loads(frappe.request.data or "{}")
    except Exception:
        return api_error("Invalid JSON payload", 400)

    lead_name = data.get("name")
    if not lead_name:
        return api_error("Lead name is required", 400)

    # Fetch Lead
    lead = frappe.get_doc("Lead", lead_name)

    # ---- BASIC INFO ----
    lead.salutation = data.get("salutation", lead.salutation)
    lead.first_name = data.get("first_name", lead.first_name)
    lead.middle_name = data.get("middle_name", lead.middle_name)
    lead.last_name = data.get("last_name", lead.last_name)
    lead.gender = data.get("gender", lead.gender)
    lead.status = data.get("status", lead.status)
    lead.source = data.get("source", lead.source)
    lead.type = data.get("lead_type", lead.type)
    lead.request_type = data.get("request_type", lead.request_type)

    # ---- CONTACT INFO ----
    lead.email_id = data.get("email", lead.email_id)
    lead.mobile_no = data.get("mobile_no", lead.mobile_no)
    lead.phone = data.get("phone", lead.phone)
    lead.whatsapp_no = data.get("whatsapp", lead.whatsapp_no)
    lead.website = data.get("website", lead.website)
    lead.phone_ext = data.get("phone_ext", lead.phone_ext)

    # ---- COMPANY INFO ----
    lead.company_name = data.get("organization_name", lead.company_name)
    lead.annual_revenue = data.get("annual_revenue", lead.annual_revenue)
    lead.no_of_employees = data.get("no_of_employees", lead.no_of_employees)
    lead.industry = data.get("industry", lead.industry)
    lead.market_segment = data.get("market_segment", lead.market_segment)

    # ---- ADDRESS ----
    lead.city = data.get("city", lead.city)
    lead.state = data.get("state", lead.state)
    lead.country = data.get("country", lead.country)
    lead.territory = data.get("territory", lead.territory)

    # ---- QUALIFICATION ----
    lead.qualification_status = data.get("qualification_status", lead.qualification_status)
    lead.qualified_by = data.get("qualified_by", lead.qualified_by)
    lead.qualified_on = data.get("qualified_on", lead.qualified_on)

    # ---- FLAGS ----
    lead.disabled = data.get("disabled", lead.disabled)
    lead.unsubscribed = data.get("unsubscribed", lead.unsubscribed)
    lead.blog_subscriber = data.get("blog_subscriber", lead.blog_subscriber)

    lead.save(ignore_permissions=True)
    frappe.db.commit()

    return api_response(
        data={"lead_id": lead.name},
        message="Lead updated successfully",
        flatten=True,
    )















@frappe.whitelist()
def delete_lead():
    """
    Delete Lead by name
    Expects JSON body with {"name": "CRM-LEAD-2025-00001"}
    """
    

    # Parse JSON safely
    try:
        data = json.loads(frappe.request.data or "{}")
    except Exception:
        frappe.throw("Invalid JSON payload")

    lead_name = data.get("name")
    if not lead_name:
        frappe.throw("Lead name is required")

    # Check if Lead exists
    if not frappe.db.exists("Lead", lead_name):
        frappe.throw(f"Lead '{lead_name}' does not exist")

    # Delete Lead
    frappe.delete_doc("Lead", lead_name, force=True)  # force=True ignores permissions for API
    frappe.db.commit()

    return {
        "status": "success",
        "status_code":200,
        "lead_id": lead_name,
        "message": "Lead deleted successfully"
    }




 

@frappe.whitelist()
def get_lead_by_id(lead_name=None):
    """
    Get a single Lead by its name (ID)
    - lead_name: Lead.name, e.g., CRM-LEAD-2025-00001
    """

    # fallback to request data
    if not lead_name:
        import json
        try:
            data = json.loads(frappe.request.data or "{}")
        except Exception:
            frappe.throw(_("Invalid JSON payload"))
        lead_name = data.get("name")

    if not lead_name:
        frappe.throw(_("Lead name is required"))

    # Check if Lead exists
    if not frappe.db.exists("Lead", lead_name):
        frappe.throw(_("Lead '{0}' does not exist").format(lead_name))

    # Fetch Lead fields
    lead = frappe.get_doc("Lead", lead_name)

    # Prepare response dictionary
    lead_data = {
        "name": lead.name,
        "salutation": lead.salutation,
        "first_name": lead.first_name,
        "middle_name": lead.middle_name,
        "last_name": lead.last_name,
        "gender": lead.gender,
        "status": lead.status,
        "source": lead.source,
        "type": lead.type,
        "request_type": lead.request_type,
        "email_id": lead.email_id,
        "mobile_no": lead.mobile_no,
        "phone": lead.phone,
        "whatsapp_no": lead.whatsapp_no,
        "website": lead.website,
        "phone_ext": lead.phone_ext,
        "company_name": lead.company_name,
        "annual_revenue": lead.annual_revenue,
        "no_of_employees": lead.no_of_employees,
        "industry": lead.industry,
        "market_segment": lead.market_segment,
        "city": lead.city,
        "state": lead.state,
        "country": lead.country,
        "territory": lead.territory,
        "qualification_status": lead.qualification_status,
        "qualified_by": lead.qualified_by,
        "qualified_on": lead.qualified_on,
        "campaign_name": lead.campaign_name,
        "company": lead.company,
        
        "disabled": lead.disabled,
        "unsubscribed": lead.unsubscribed,
        "blog_subscriber": lead.blog_subscriber,
        "creation": lead.creation,
        "modified": lead.modified
    }

    return {
        "status": "success",
        "message": "Lead fetched successfully",
        "data": lead_data
    }












@frappe.whitelist()
def convert_lead_to_opportunity():
    """
    Convert Lead to Opportunity
    Expects JSON body: {"lead_name": "CRM-LEAD-2025-00002"}
    """
    import json

    # Parse JSON safely
    try:
        data = json.loads(frappe.request.data or "{}")
    except Exception:
        frappe.throw(_("Invalid JSON payload"))

    lead_name = data.get("lead_name")
    if not lead_name:
        frappe.throw(_("Lead name is required"))

    # Check if Lead exists
    if not frappe.db.exists("Lead", lead_name):
        frappe.throw(_("Lead '{0}' does not exist").format(lead_name))

    # Import ERPNext helper
    from erpnext.crm.doctype.lead.lead import make_opportunity

    try:
        # Create Opportunity from Lead
        opportunity = make_opportunity(lead_name)

        # Insert / save if not already inserted
        if not opportunity.get("name"):
            opportunity.insert(ignore_permissions=True)
        else:
            opportunity.save(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "status_code":201,
            "opportunity_id": opportunity.name,
            "message": _("Lead converted to Opportunity successfully")
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Lead Conversion Failed"))
        frappe.throw(_("Failed to convert lead to opportunity: {0}").format(str(e)))
