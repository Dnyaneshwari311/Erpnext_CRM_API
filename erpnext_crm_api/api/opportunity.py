import frappe
from frappe import _

@frappe.whitelist()
def create_opportunity(data=None):
    try:
        # ✅ Accept both JSON body & form_dict
        if not data:
            data = frappe.form_dict

        if isinstance(data, str):
            data = frappe.parse_json(data)

        # 🔹 Mandatory validation
        required_fields = [
            "opportunity_from",
            "party_name",
            "status",
            "company",
            "opportunity_date"
        ]

        for field in required_fields:
            if not data.get(field):
                frappe.throw(_(f"{field} is required"))

        opp = frappe.new_doc("Opportunity")

        # 🔹 Core Fields
        opp.opportunity_type = data.get("opportunity_type")
        opp.sales_stage = data.get("sales_stage")
        opp.opportunity_from = data.get("opportunity_from")
        opp.party_name = data.get("party")
        opp.source = data.get("source")
        opp.expected_closing_date = data.get("expected_closing_date")
        opp.opportunity_owner = data.get("opportunity_owner")
        opp.probability = data.get("probability")
        opp.status = data.get("status")
        opp.company = data.get("company")
        opp.opportunity_date = data.get("opportunity_date")
        opp.campaign = data.get("campaign")

        # 🔹 Organization Details
        opp.no_of_employees = data.get("no_of_employees")
        opp.industry = data.get("industry")
        opp.annual_revenue = data.get("annual_revenue")
        opp.market_segment = data.get("market_segment")

        # 🔹 Address
        opp.city = data.get("city")
        opp.state = data.get("state")
        opp.country = data.get("country")
        opp.territory = data.get("territory")
        opp.website = data.get("website")

        # 🔹 Currency
        opp.currency = data.get("currency")
        opp.exchange_rate = data.get("exchange_rate")
        opp.opportunity_amount = data.get("opportunity_amount")

        # 🔹 Contact Details
        opp.job_title = data.get("job_title")
        opp.contact_email = data.get("contact_email")
        opp.contact_mobile = data.get("contact_mobile")
        opp.whatsapp = data.get("whatsapp")
        opp.phone = data.get("phone")
        opp.phone_ext = data.get("phone_ext")

        # 🔹 Items
        for item in data.get("items", []):
            opp.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "rate": item.get("rate"),
                "amount": item.get("amount")
            })

        opp.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "status_code":201,
            "message": "Opportunity created successfully",
            "opportunity_id": opp.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Opportunity API Error")
        return {
            "status": "error",
            "message": str(e)
        }












# @frappe.whitelist()
# def list_opportunity(
#     page=1,
#     page_size=10,
#     sort_by="modified",
#     sort_order="desc",
#     search=None,
#     status=None,
#     source=None,
#     opportunity_from=None,
#     company=None
# ):
#     page = int(page)
#     page_size = int(page_size)
#     start = (page - 1) * page_size

#     # -------------------------
#     # AND filters
#     # -------------------------
#     filters = {}
#     if status:
#         filters["status"] = status
#     if source:
#         filters["source"] = source
#     if opportunity_from:
#         filters["opportunity_from"] = opportunity_from
#     if company:
#         filters["company"] = company

#     # -------------------------
#     # OR filters (search)
#     # -------------------------
#     or_filters = []
#     if search:
#         or_filters = [
#             ["Opportunity", "party_name", "like", f"%{search}%"],
#             ["Opportunity", "contact_email", "like", f"%{search}%"],
#             ["Opportunity", "contact_mobile", "like", f"%{search}%"],
#             ["Opportunity", "source", "like", f"%{search}%"],
#             ["Opportunity", "company", "like", f"%{search}%"],
#         ]

#     # -------------------------
#     # DATA QUERY
#     # -------------------------
#     opportunities = frappe.get_all(
#         "Opportunity",
#         fields=[
#             "name",
#             "party_name",
#             "status",
#             "source",
#             "opportunity_from",
#             "company",
#             "transaction_date",
#             "opportunity_amount",
#             "sales_stage",
#             "modified"
#         ],
#         filters=filters,
#         or_filters=or_filters,
#         order_by=f"{sort_by} {sort_order}",
#         limit_start=start,
#         limit_page_length=page_size
#     )

#     # -------------------------
#     # TOTAL COUNT (supports OR)
#     # -------------------------
#     total_count = len(
#         frappe.get_all(
#             "Opportunity",
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
#         "data": opportunities
#     }





@frappe.whitelist()
def list_opportunity(
    page=1,
    page_size=10,
    sort_by="modified",
    sort_order="desc",
    search=None,
    status=None,
    source=None,
    opportunity_from=None,
    company=None
):
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -------------------------
    # AND filters
    # -------------------------
    filters = {}
    if status:
        filters["status"] = status
    if source:
        filters["source"] = source
    if opportunity_from:
        filters["opportunity_from"] = opportunity_from
    if company:
        filters["company"] = company

    # -------------------------
    # OR filters (search)
    # -------------------------
    or_filters = []
    if search:
        or_filters = [
            ["Opportunity", "party_name", "like", f"%{search}%"],
            ["Opportunity", "contact_email", "like", f"%{search}%"],
            ["Opportunity", "contact_mobile", "like", f"%{search}%"],
            ["Opportunity", "source", "like", f"%{search}%"],
            ["Opportunity", "company", "like", f"%{search}%"],
        ]

    # -------------------------
    # DATA QUERY (ALL FIELDS)
    # -------------------------
    opportunities = frappe.get_all(
        "Opportunity",
        fields=["*"],   # ✅ ALL fields
        filters=filters,
        or_filters=or_filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # -------------------------
    # TOTAL COUNT (OR supported)
    # -------------------------
    total_count = len(
        frappe.get_all(
            "Opportunity",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    total_pages = (total_count + page_size - 1) // page_size

    return {
        "status": "success",
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,
        "data": opportunities
    }



# @frappe.whitelist()
# def update_opportunity(opportunity_id=None, data=None):
#     try:
#         if not opportunity_id:
#             frappe.throw(_("opportunity_id is required"))

#         # Accept JSON body or form_dict
#         if not data:
#             data = frappe.form_dict

#         if isinstance(data, str):
#             data = frappe.parse_json(data)

#         # Get existing Opportunity
#         opp = frappe.get_doc("Opportunity", opportunity_id)

#         # -------------------------
#         # UPDATE opportunity_from FIRST
#         # -------------------------
#         if data.get("opportunity_from"):
#             opp.opportunity_from = data.get("opportunity_from")

#         opportunity_from = opp.opportunity_from
#         party_name = data.get("party_name")
#         email = data.get("contact_email")

#         # -------------------------
#         # PARTY HANDLING
#         # -------------------------
#         if party_name:
#             if opportunity_from == "Lead":
#                 # Look for Lead by email
#                 lead_name = frappe.db.get_value("Lead", {"email_id": email})
#                 if not lead_name:
#                     # Create Lead if it does not exist
#                     first_name = party_name.split()[0]
#                     last_name = " ".join(party_name.split()[1:]) if len(party_name.split()) > 1 else ""
#                     lead = frappe.get_doc({
#                         "doctype": "Lead",
#                         "first_name": first_name,
#                         "last_name": last_name,
#                         "email_id": email,
#                         "mobile_no": data.get("contact_mobile"),
#                         "company_name": data.get("organization_name"),
#                         "status": "Lead"
#                     })
#                     lead.insert(ignore_permissions=True)
#                     frappe.db.commit()
#                     lead_name = lead.name

#                 # Assign Lead record name to party (must be record name)
#                 opp.party = lead_name
#                 opp.party_name = party_name

#             elif opportunity_from == "Customer":
#                 if not frappe.db.exists("Customer", party_name):
#                     frappe.throw(_("Customer '{0}' does not exist").format(party_name))
#                 opp.party = party_name
#                 opp.party_name = party_name

#         # -------------------------
#         # FIELD UPDATE (partial)
#         # -------------------------
#         skip_fields = ["name", "doctype", "items", "opportunity_id", "party_name"]
#         for field, value in data.items():
#             if field in skip_fields:
#                 continue
#             if opp.meta.get_field(field):
#                 opp.set(field, value)

#         # -------------------------
#         # ITEMS UPDATE (replace)
#         # -------------------------
#         if "items" in data:
#             opp.items = []
#             for item in data.get("items", []):
#                 opp.append("items", {
#                     "item_code": item.get("item_code"),
#                     "qty": item.get("qty"),
#                     "rate": item.get("rate"),
#                     "amount": item.get("amount")
#                 })

#         # Save and commit
#         opp.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "status_code":200,
#             "message": "Opportunity updated successfully",
#             "opportunity_id": opp.name
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Update Opportunity API Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }

@frappe.whitelist()
def update_opportunity(opportunity_id=None, data=None):
    import json
    try:
        if not opportunity_id:
            frappe.throw(_("opportunity_id is required"))

        # -------------------------
        # Ensure data is always a dict
        # -------------------------
        if not data:
            parsed_data = {}
        elif isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except Exception:
                frappe.throw(_("Invalid JSON payload"))
        elif isinstance(data, dict):
            parsed_data = data
        else:
            parsed_data = {}

        # -------------------------
        # Fetch Opportunity
        # -------------------------
        opp = frappe.get_doc("Opportunity", opportunity_id)

        if not opp.party_name:
            frappe.throw(_("Opportunity does not have a Lead/Customer assigned"))

        linked_party = opp.party_name

        # Verify Lead or Customer exists
        if opp.opportunity_from == "Lead":
            if not frappe.db.exists("Lead", linked_party):
                frappe.throw(_("Lead '{0}' does not exist").format(linked_party))
        elif opp.opportunity_from == "Customer":
            if not frappe.db.exists("Customer", linked_party):
                frappe.throw(_("Customer '{0}' does not exist").format(linked_party))

        # -------------------------
        # Update other fields
        # -------------------------
        skip_fields = ["name", "doctype", "items", "opportunity_id", "party_name", "opportunity_from"]

        for field, value in parsed_data.items():
            if field in skip_fields:
                continue
            if opp.meta.get_field(field):
                opp.set(field, value)

        # -------------------------
        # Update items
        # -------------------------
        items = parsed_data.get("items") or []
        if isinstance(items, list):
            opp.items = []
            for item in items:
                opp.append("items", {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "rate": item.get("rate"),
                    "amount": item.get("amount")
                })

        # -------------------------
        # Save
        # -------------------------
        opp.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 200,
            "message": "Opportunity updated successfully",
            "opportunity_id": opp.name,
            # "linked_party": linked_party
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Opportunity API Error")
        return {
            "status": "error",
            "message": str(e)
        }

        
@frappe.whitelist()
def delete_opportunity(opportunity_id=None):
    try:
        if not opportunity_id:
            frappe.throw(_("opportunity_id is required"))

        frappe.delete_doc(
            "Opportunity",
            opportunity_id,
            ignore_permissions=True
        )
        frappe.db.commit()

        return {
            "status": "success",
            "status_code":200,
            "message": "Opportunity deleted successfully",
            "opportunity_id": opportunity_id
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Opportunity API Error")
        return {
            "status": "error",
            "message": str(e)
        }











@frappe.whitelist()
def get_opportunity(name=None):
    """
    Fetch a single Opportunity by its name
    """
    try:
        if not name:
            frappe.throw(_("name is required"))

        # Fetch Opportunity
        opp = frappe.get_doc("Opportunity", name)

        # Convert doc to dict
        data = opp.as_dict()

        # Ensure items are included
        data["items"] = [item.as_dict() for item in opp.items]

        return {
            "status": "success",
            "message": "Opportunity fetched successfully",
            "name": opp.name,   # ✅ explicitly returning name
            "data": data
        }

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": _("Opportunity with name '{0}' does not exist").format(name)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Opportunity API Error")
        return {
            "status": "error",
            "message": str(e)
        }






from frappe.utils import nowdate, add_days


@frappe.whitelist()
def create_quotation_from_opportunity(opportunity_id=None, valid_till=None, submit=0):
    try:
        if not opportunity_id:
            frappe.throw(_("opportunity_id is required"))

        submit = int(submit)

        opp = frappe.get_doc("Opportunity", opportunity_id)

        if not opp.items:
            frappe.throw(_("Opportunity has no items"))

        quotation = frappe.new_doc("Quotation")

        quotation.opportunity = opp.name
        quotation.company = opp.company
        quotation.currency = opp.currency
        quotation.conversion_rate = 1
        quotation.transaction_date = nowdate()
        quotation.valid_till = valid_till or add_days(nowdate(), 30)

        quotation.selling_price_list = frappe.get_cached_value(
            "Company", quotation.company, "default_selling_price_list"
        )

        # PARTY
        if opp.opportunity_from == "Customer":
            quotation.quotation_to = "Customer"
            quotation.party_name = opp.party_name
            quotation.customer_name = opp.customer_name

        elif opp.opportunity_from == "Lead":
            quotation.quotation_to = "Lead"
            quotation.party_name = opp.party_name
            quotation.lead_name = opp.party_name

        else:
            frappe.throw(_("Unsupported opportunity_from type"))

        # ITEMS
        for item in opp.items:
            quotation.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount,
                "uom": item.uom
            })

        # 🚫 NO TAX COPYING (Opportunity has none)

        quotation.insert(ignore_permissions=True)

        if submit:
            quotation.submit()

        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 201,
            "message": "Opportunity converted to Quotation successfully",
            "quotation_id": quotation.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Opportunity → Quotation API Error")
        return {
            "status": "error",
            "message": str(e)
        }
