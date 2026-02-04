import frappe
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error

@frappe.whitelist()
def create_quotation(data=None):

    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    doc = frappe.new_doc("Quotation")

    # ===== BASIC =====
    doc.naming_series = data.get("series")
    doc.transaction_date = data.get("date")
    doc.valid_till = data.get("valid_till")
    doc.order_type = data.get("order_type")
    doc.quotation_to = data.get("quotation_to")  # Customer / Supplier

    # party_name = data.get("customer")

    # if not party_name:
    #     frappe.throw("Customer / Supplier is required")

    # # ❌ DO NOT CREATE CUSTOMER / SUPPLIER
    # if doc.quotation_to == "Customer":
    #     if not frappe.db.exists("Customer", party_name):
    #         frappe.throw(f"Customer '{party_name}' does not exist")
    #     doc.party_name = party_name

    # elif doc.quotation_to == "Supplier":
    #     if not frappe.db.exists("Supplier", party_name):
    #         frappe.throw(f"Supplier '{party_name}' does not exist")
    #     doc.party_name = party_name

    # else:
    #     frappe.throw("Invalid quotation_to value")
    
    
    
    party_name = data.get("customer")

    if not party_name:
        # frappe.throw("Customer / Lead / Supplier is required")
        return api_error(
            "Customer / Lead / Supplier is required",400)

    if doc.quotation_to == "Customer":
        if not frappe.db.exists("Customer", party_name):
            return api_error(
                f"Customer '{party_name}' does not exist",400)
            
        doc.party_name = party_name

    elif doc.quotation_to == "Supplier":
        if not frappe.db.exists("Supplier", party_name):
            return api_error(
                f"Supplier '{party_name}' does not exist",400)
        doc.party_name = party_name

    elif doc.quotation_to == "Lead":
        if not frappe.db.exists("Lead", party_name):
            return api_error(
                f"Lead '{party_name}' does not exist",400)
        doc.party_name = party_name
        doc.lead = party_name   # 🔥 VERY IMPORTANT

    else:
        return api_error(
            "Invalid quotation_to value",400)

        
        
    

    doc.company = data.get("company")
    doc.status = data.get("status", "Draft")

    # ===== CURRENCY =====
    doc.currency = data.get("currency")
    doc.selling_price_list = data.get("price_list")
    doc.conversion_rate = data.get("exchange_rate")
    doc.ignore_pricing_rule = data.get("ignore_pricing_rule")

    # ===== ITEMS =====
    if not data.get("items"):
        return api_error(
            "Quotation must have at least one item",400)

    for row in data.get("items"):
        doc.append("items", {
            "item_code": row.get("item_code"),
            "qty": row.get("quantity"),
            "rate": row.get("rate")
        })

    # ===== TAXES =====
    for tax in data.get("sales_taxes_and_charges", []):
        doc.append("taxes", {
            "charge_type": tax.get("type"),
            "account_head": tax.get("account_head"),
            "rate": tax.get("tax_rate")
        })

    # ===== DISCOUNTS =====
    doc.apply_discount_on = data.get("apply_additional_discount_on")
    doc.additional_discount_percentage = data.get("additional_discount_percentage")
    doc.additional_discount_amount = data.get("additional_discount_amount")

    # ===== ADDRESS =====
    doc.customer_address = data.get("lead_address")
    doc.contact_person = data.get("contact_person")
    doc.shipping_address_name = data.get("shipping_address")
    doc.company_address = data.get("company_address_name")

    # ===== PAYMENT =====
    doc.payment_terms_template = data.get("payment_terms_template")
    for p in data.get("payment_schedule", []):
        doc.append("payment_schedule", p)

    # ===== TERMS =====
    doc.terms = data.get("terms")
    doc.terms_and_conditions = data.get("term_details")

    frappe.local.flags.ignore_messages = True

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return api_response(
    data={
        "quotation": doc.name
    },
    message=_("Quotation created successfully"),
    status_code=201,
    flatten=True
)






@frappe.whitelist()
def submit_quotation(quotation_name):
    try:
        doc = frappe.get_doc("Quotation", quotation_name)

        # ERPNext rule
        if doc.docstatus != 0:
            return api_error(
                "Only Draft quotations can be submitted",400
            )

        doc.submit()
        frappe.db.commit()

        return api_response(
        data={
            "quotation": doc.name,
            "docstatus": doc.docstatus,          # 1
            "quotation_status": doc.status       # Open
        },
        message=_("Quotation Submitted Successfully"),
        status_code=200,
        flatten=True
    )


    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Submit Quotation API Error")
        return api_error(str(e), 403)






@frappe.whitelist()
def cancel_quotation(quotation_name):
    try:
        # Fetch quotation
        doc = frappe.get_doc("Quotation", quotation_name)

        # Validate state
        if doc.docstatus != 1:
            # return {
            #     "status": "error",
            #     "message": "Only Submitted quotations can be cancelled"
            # }
            return api_error(
                "Only Submitted quotations can be cancelled",400
            )

        # Cancel quotation
        doc.cancel()
        frappe.db.commit()
        return api_response(
        data={
            "quotation": doc.name,
            "docstatus": doc.docstatus,          # 2
            "quotation_status": doc.status       # Cancelled
        },
        message=_("Quotation Cancelled Successfully"),
        status_code=200,
        flatten=True
    )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Quotation API Error")
        return api_error(str(e), 403)




@frappe.whitelist()
def delete_quotation(quotation_name):
    try:
        # Fetch quotation
        doc = frappe.get_doc("Quotation", quotation_name)

        # Only Draft can be deleted
        if doc.docstatus != 0:
            return api_error(
                "Only Draft quotations can be deleted. Cancel the document instead.",400
            )

        # Delete quotation
        frappe.delete_doc(
            doctype="Quotation",
            name=quotation_name,
            ignore_permissions=True,
            force=True
        )

        frappe.db.commit()
        return api_response(
        data={
            "quotation": quotation_name
        },
        message=_("Quotation Deleted Successfully"),
        status_code=200,
        flatten=True
    )

    except frappe.DoesNotExistError:
        return api_error(
            "Quotation not found",404
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Quotation API Error")
        return api_error(str(e), 403)







@frappe.whitelist()
def update_quotation(data=None):
    """
    Update an existing Quotation by name.
    Expects 'name' in data.
    """
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    quotation_name = data.get("name")
    if not quotation_name:
        return api_error("Quotation name is required for update",400)

    if not frappe.db.exists("Quotation", quotation_name):
        return api_error(f"Quotation {quotation_name} does not exist",404)

    doc = frappe.get_doc("Quotation", quotation_name)

    # ===== BASIC =====
    doc.transaction_date = data.get("date") or doc.transaction_date
    doc.valid_till = data.get("valid_till") or doc.valid_till
    doc.order_type = data.get("order_type") or doc.order_type
    doc.quotation_to = data.get("quotation_to") or doc.quotation_to

    party_name = data.get("customer") or doc.party_name
    if doc.quotation_to == "Customer":
        if not frappe.db.exists("Customer", party_name):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": party_name
            }).insert(ignore_permissions=True)
    elif doc.quotation_to == "Supplier":
        if not frappe.db.exists("Supplier", party_name):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": party_name
            }).insert(ignore_permissions=True)
    doc.party_name = party_name

    doc.company = data.get("company") or doc.company
    doc.status = data.get("status") or doc.status

    # ===== CURRENCY =====
    doc.currency = data.get("currency") or doc.currency
    doc.selling_price_list = data.get("price_list") or doc.selling_price_list
    doc.conversion_rate = data.get("exchange_rate") or doc.conversion_rate
    doc.ignore_pricing_rule = data.get("ignore_pricing_rule") or doc.ignore_pricing_rule
    doc.scan_barcode = data.get("scan_barcode") or doc.scan_barcode

    # ===== ITEMS =====
    if "items" in data:
        doc.items = []
        for row in data.get("items", []):
            item_code = row.get("item_code")
            if not frappe.db.exists("Item", item_code):
                frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_code,
                    "item_name": item_code,
                    "stock_uom": "Nos",
                    "is_stock_item": 0
                }).insert(ignore_permissions=True)
            doc.append("items", {
                "item_code": item_code,
                "qty": row.get("quantity"),
                "rate": row.get("rate")
            })

    # ===== TAXES =====
    if "sales_taxes_and_charges" in data:
        doc.taxes = []
        for tax in data.get("sales_taxes_and_charges", []):
            doc.append("taxes", {
                "charge_type": tax.get("type"),
                "account_head": tax.get("account_head"),
                "rate": tax.get("tax_rate")
            })

    # ===== DISCOUNTS =====
    doc.apply_discount_on = data.get("apply_additional_discount_on") or doc.apply_discount_on
    doc.additional_discount_percentage = data.get("additional_discount_percentage") or doc.additional_discount_percentage
    doc.additional_discount_amount = data.get("additional_discount_amount") or doc.additional_discount_amount
    doc.coupon_code = data.get("coupon_code") or doc.coupon_code

    # ===== ADDRESS =====
    doc.customer_address = data.get("lead_address") or doc.customer_address
    doc.contact_person = data.get("contact_person") or doc.contact_person
    doc.place_of_supply = data.get("place_of_supply") or doc.place_of_supply
    doc.shipping_address_name = data.get("shipping_address") or doc.shipping_address_name
    doc.company_address = data.get("company_address_name") or doc.company_address
    doc.company_contact_person = data.get("company_contact_person") or doc.company_contact_person

    # ===== PAYMENT =====
    doc.payment_terms_template = data.get("payment_terms_template") or doc.payment_terms_template
    if "payment_schedule" in data:
        doc.payment_schedule = []
        for p in data.get("payment_schedule", []):
            doc.append("payment_schedule", p)

    # ===== TERMS =====
    doc.terms = data.get("terms") or doc.terms
    doc.terms_and_conditions = data.get("term_details") or doc.terms_and_conditions

    # ===== PRINT =====
    doc.letter_head = data.get("letter_head") or doc.letter_head
    doc.print_heading = data.get("print_heading") or doc.print_heading
    doc.group_same_items = data.get("group_same_items") or doc.group_same_items

    # ===== EXTRA =====
    doc.referral_sales_partner = data.get("referral_sales_partner") or doc.referral_sales_partner
    doc.supplier_quotation = data.get("supplier_quotation") or doc.supplier_quotation
    doc.territory = data.get("territory") or doc.territory
    doc.source = data.get("source") or doc.source
    doc.campaign = data.get("campaign") or doc.campaign

    # 🔹 Suppress server messages
    frappe.local.flags.ignore_messages = True

    # 🔹 Save Quotation
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return api_response(
    data={
        "quotation": doc.name
    },
    message=_("Quotation Updated Successfully"),
    status_code=200,
    flatten=True
)









@frappe.whitelist()
def list_quotation(
    page=1,
    page_size=10,
    sort_by="modified",
    sort_order="desc",
    search=None,
    status=None,
    quotation_to=None,   # Customer / Supplier
    company=None,
    customer=None
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
    if quotation_to:
        filters["quotation_to"] = quotation_to
    if company:
        filters["company"] = company
    if customer:
        filters["party_name"] = customer

    # -------------------------
    # OR filters (search)
    # -------------------------
    or_filters = []
    if search:
        or_filters = [
            ["Quotation", "name", "like", f"%{search}%"],
            ["Quotation", "party_name", "like", f"%{search}%"],
            ["Quotation", "company", "like", f"%{search}%"],
            ["Quotation", "status", "like", f"%{search}%"],
            ["Quotation", "quotation_to", "like", f"%{search}%"],
        ]

    # -------------------------
    # DATA QUERY
    # -------------------------
    quotations = frappe.get_all(
        "Quotation",
        fields=[
            "name",
            "transaction_date",
            "valid_till",
            "quotation_to",
            "party_name",
            "company",
            "status",
            "grand_total",
            "currency",
            "modified"
        ],
        filters=filters,
        or_filters=or_filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # -------------------------
    # TOTAL COUNT (supports OR)
    # -------------------------
    total_count = len(
        frappe.get_all(
            "Quotation",
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
            "total_records": total_count,
            "total_pages": total_pages,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "data": quotations
        },
        message=_("Quotations List Fetched Successfully"),
        status_code=200,
        flatten=True
    )







@frappe.whitelist()
def get_quotation_by_id(name=None):
    """
    Fetch a single Quotation by its name (ID)
    """
    try:
        if not name:
            # return {
            #     "status": "error",
            #     "message": "Quotation name is required"
            # }
            return api_error(
                "Quotation name is required",400
            )

        doc = frappe.get_doc("Quotation", name)


        return api_response(
        data={
            "name": doc.name,
            "transaction_date": doc.transaction_date,
            "valid_till": doc.valid_till,
            "quotation_to": doc.quotation_to,
            "party_name": doc.party_name,
            "company": doc.company,
            "status": doc.status,
            "currency": doc.currency,
            "grand_total": doc.grand_total,
            "items": [
                {
                    "item_code": i.item_code,
                    "qty": i.qty,
                    "rate": i.rate,
                    "amount": i.amount
                }
                for i in doc.items
            ],
            "taxes": [
                {
                    "charge_type": t.charge_type,
                    "account_head": t.account_head,
                    "rate": t.rate,
                    "tax_amount": t.tax_amount
                }
                for t in doc.taxes
            ],
            "payment_schedule": [
                {
                    "payment_term": p.payment_term,
                    "due_date": p.due_date,
                    "expected_amount": p.payment_amount
                }
                for p in doc.payment_schedule
            ]
        },
        message=_("Quotation Fetched Successfully"),
        status_code=200,
        flatten=True
    )

    except frappe.DoesNotExistError:
        return api_error(
            f"Quotation {name} does not exist",404
        )
        

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Quotation By ID Error")
        return api_error(str(e), 403)










@frappe.whitelist()
def get_quotation_items(name=None):
    """
    Fetch items for a specific Quotation by name
    """
    try:
        if not name:
            return api_error("Quotation name is required", 400)

        doc = frappe.get_doc("Quotation", name)
        items = [
            {
                "item_code": i.item_code,
                "item_name": i.item_name,
                "description": i.description,
                "qty": i.qty,
                "rate": i.rate,
                "amount": i.amount
            }
            for i in doc.items
        ]
        return api_response(
            data=items,
            message=_("Quotation Items Fetched Successfully"),
            status_code=200,
            flatten=True
        )
    except frappe.DoesNotExistError:
        return api_error(f"Quotation {name} does not exist", 404)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Quotation Items Error")
        return api_error(str(e), 403)







def create_sales_order_from_quotation(quotation_name=None, submit=0):
    try:
        if not quotation_name:
            frappe.throw("quotation_name is required")
            
            

        submit = int(submit)
        quotation = frappe.get_doc("Quotation", quotation_name)

        # -----------------------
        # VALIDATIONS
        # -----------------------
        if quotation.docstatus != 1:
            frappe.throw("Only Submitted Quotations can be converted")

        # -----------------------
        # HANDLE CUSTOMER / LEAD
        # -----------------------
        if quotation.quotation_to == "Customer":
            customer = quotation.party_name
            if not customer:
                frappe.throw("Quotation has no customer")
            if not frappe.db.exists("Customer", customer):
                frappe.throw(f"Customer '{customer}' does not exist")

        elif quotation.quotation_to == "Lead":
            # Try to find existing Customer linked to Lead
            customer = frappe.db.get_value("Customer", {"lead_name": quotation.party_name})
            if not customer:
                # Create Customer from Lead
                lead_doc = frappe.get_doc("Lead", quotation.party_name)
                customer_doc = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": lead_doc.lead_name,
                    "lead_name": lead_doc.name,
                    "company": quotation.company
                })
                customer_doc.insert(ignore_permissions=True)
                customer = customer_doc.name
        else:
            frappe.throw(f"Quotation type '{quotation.quotation_to}' not supported")

        # -----------------------
        # CREATE SALES ORDER
        # -----------------------
        so = frappe.new_doc("Sales Order")
        so.customer = customer
        so.customer_name = frappe.get_cached_value("Customer", customer, "customer_name")
        so.company = quotation.company
        so.transaction_date = frappe.utils.nowdate()
        so.delivery_date = quotation.valid_till
        so.currency = quotation.currency
        so.conversion_rate = quotation.conversion_rate or 1
        so.selling_price_list = quotation.selling_price_list

        # -----------------------
        # ITEMS
        # -----------------------
        for qi in quotation.items:
            so.append("items", {
                "item_code": qi.item_code,
                "item_name": qi.item_name,
                "description": qi.description,
                "qty": qi.qty,
                "rate": qi.rate,
                "uom": qi.uom,
                "conversion_factor": qi.conversion_factor or 1,
                "quotation": quotation.name,
                "quotation_item": qi.name
            })

        # -----------------------
        # TAXES
        # -----------------------
        if quotation.taxes:
            for t in quotation.taxes:
                so.append("taxes", {
                    "charge_type": t.charge_type,
                    "account_head": t.account_head,
                    "rate": t.rate
                })

        frappe.local.flags.ignore_messages = True
        so.insert(ignore_permissions=True)

        if submit:
            so.submit()

        frappe.db.commit()

        return {
            "status": "success",
            "status_code": 200,
            "sales_order": so.name,
            "message": "Sales Order created successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Quotation → Sales Order Error")
        return {
            "status": "error",
            "message": str(e)
        }





from frappe.utils.pdf import get_pdf

@frappe.whitelist(allow_guest=True)
def download_quotation_pdf(quotation_name):
    """
    Download Quotation PDF using custom print format
    """

    if not quotation_name:
        frappe.throw("Quotation name is required")

    html = frappe.get_print(
        doctype="Quotation",
        name=quotation_name,
        print_format="Print Format For Quotation",  # <-- your print format name
        as_pdf=False
    )

    pdf_data = get_pdf(html)

    frappe.local.response = frappe._dict()
    frappe.local.response.filecontent = pdf_data
    frappe.local.response.filename = f"QUOTATION_{quotation_name}.pdf"
    frappe.local.response.type = "download"
