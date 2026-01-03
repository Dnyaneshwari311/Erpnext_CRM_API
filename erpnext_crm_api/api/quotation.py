import frappe

@frappe.whitelist()
def create_quotation(data=None):
    # 🔹 If data not passed explicitly, read from request body
    if not data:
        data = frappe.form_dict

    # 🔹 If data is JSON string, parse it
    if isinstance(data, str):
        data = frappe.parse_json(data)

    doc = frappe.new_doc("Quotation")

    # ===== BASIC =====
    doc.naming_series = data.get("series")
    doc.transaction_date = data.get("date")
    doc.valid_till = data.get("valid_till")
    doc.order_type = data.get("order_type")
    doc.quotation_to = data.get("quotation_to")  # "Customer" or "Supplier"

    party_name = data.get("customer")
    if doc.quotation_to == "Customer":
        # Create Customer if not exists
        if not frappe.db.exists("Customer", party_name):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": party_name
            }).insert(ignore_permissions=True)
    elif doc.quotation_to == "Supplier":
        # Create Supplier if not exists
        if not frappe.db.exists("Supplier", party_name):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": party_name
            }).insert(ignore_permissions=True)

    doc.party_name = party_name
    doc.company = data.get("company")
    doc.status = data.get("status", "Draft")

    # ===== CURRENCY =====
    doc.currency = data.get("currency")
    doc.selling_price_list = data.get("price_list")
    doc.conversion_rate = data.get("exchange_rate")
    doc.ignore_pricing_rule = data.get("ignore_pricing_rule")
    doc.scan_barcode = data.get("scan_barcode")

    # ===== ITEMS =====
    for row in data.get("items", []):
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
    doc.coupon_code = data.get("coupon_code")

    # ===== ADDRESS =====
    doc.customer_address = data.get("lead_address")
    doc.contact_person = data.get("contact_person")
    doc.place_of_supply = data.get("place_of_supply")
    doc.shipping_address_name = data.get("shipping_address")
    doc.company_address = data.get("company_address_name")
    doc.company_contact_person = data.get("company_contact_person")

    # ===== PAYMENT =====
    doc.payment_terms_template = data.get("payment_terms_template")
    for p in data.get("payment_schedule", []):
        doc.append("payment_schedule", p)

    # ===== TERMS =====
    doc.terms = data.get("terms")
    doc.terms_and_conditions = data.get("term_details")

    # ===== PRINT =====
    doc.letter_head = data.get("letter_head")
    doc.print_heading = data.get("print_heading")
    doc.group_same_items = data.get("group_same_items")

    # ===== EXTRA =====
    doc.referral_sales_partner = data.get("referral_sales_partner")
    doc.supplier_quotation = data.get("supplier_quotation")
    doc.territory = data.get("territory")
    doc.source = data.get("source")
    doc.campaign = data.get("campaign")
    
    frappe.local.flags.ignore_messages = True
    # 🔹 Insert Quotation
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "status_code":201,
        "quotation": doc.name,
        "message": "Quotation Created Successfully"
    }









@frappe.whitelist()
def submit_quotation(quotation_name):
    try:
        doc = frappe.get_doc("Quotation", quotation_name)

        # ERPNext rule
        if doc.docstatus != 0:
            return {
                "status": "error",
                "message": "Only Draft quotations can be submitted"
            }

        doc.submit()
        frappe.db.commit()

        return {
            "status": "success",
            "quotation": doc.name,
            "docstatus": doc.docstatus,   # 1
            "quotation_status": doc.status,  # Open
            "message": "Quotation Submitted Successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Submit Quotation API Error")
        return {
            "status": "error",
            "message": str(e)
        }






@frappe.whitelist()
def cancel_quotation(quotation_name):
    try:
        # Fetch quotation
        doc = frappe.get_doc("Quotation", quotation_name)

        # Validate state
        if doc.docstatus != 1:
            return {
                "status": "error",
                "message": "Only Submitted quotations can be cancelled"
            }

        # Cancel quotation
        doc.cancel()
        frappe.db.commit()

        return {
            "status": "success",
            "quotation": doc.name,
            "docstatus": doc.docstatus,
            "quotation_status": doc.status,
            "message": "Quotation Cancelled Successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Quotation API Error")
        return {
            "status": "error",
            "message": str(e)
        }




@frappe.whitelist()
def delete_quotation(quotation_name):
    try:
        # Fetch quotation
        doc = frappe.get_doc("Quotation", quotation_name)

        # Only Draft can be deleted
        if doc.docstatus != 0:
            return {
                "status": "error",
                "message": "Only Draft quotations can be deleted. Cancel the document instead."
            }

        # Delete quotation
        frappe.delete_doc(
            doctype="Quotation",
            name=quotation_name,
            ignore_permissions=True,
            force=True
        )

        frappe.db.commit()

        return {
            "status": "success",
            "quotation": quotation_name,
            "message": "Quotation Deleted Successfully"
        }

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": "Quotation not found"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Quotation API Error")
        return {
            "status": "error",
            "message": str(e)
        }







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
        frappe.throw("Quotation name is required for update")

    if not frappe.db.exists("Quotation", quotation_name):
        frappe.throw(f"Quotation {quotation_name} does not exist")

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

    return {
        "status": "success",
        "quotation": doc.name,
        "message": "Quotation Updated Successfully"
    }









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

    return {
        "status": "success",

        # pagination info
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "total_pages": total_pages,

        # navigation helpers
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,

        # actual data
        "data": quotations
    }











@frappe.whitelist()
def get_quotation_by_id(name=None):
    """
    Fetch a single Quotation by its name (ID)
    """
    try:
        if not name:
            return {
                "status": "error",
                "message": "Quotation name is required"
            }

        doc = frappe.get_doc("Quotation", name)

        return {
            "status": "success",
            "message": "Quotation fetched successfully",
            "data": {
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
            }
        }

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": f"Quotation {name} does not exist"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Quotation By ID Error")
        return {
            "status": "error",
            "message": str(e)
        }
