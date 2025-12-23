import frappe
from frappe.utils import nowdate, nowtime

@frappe.whitelist(methods=["POST"])
def create_delivery_note(data=None):
    """
    Create Delivery Note (Draft) as per ERPNext standard flow
    """

    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        dn = frappe.new_doc("Delivery Note")

        # -------------------------
        # Basic Details
        # -------------------------
        dn.posting_date = data.get("date") or nowdate()
        dn.posting_time = data.get("posting_time") or nowtime()
        dn.company = data.get("company")
        dn.customer = data.get("customer")
        dn.currency = data.get("currency")
        dn.price_list = data.get("price_list")
        dn.exchange_rate = data.get("exchange_rate", 1)
        dn.is_return = data.get("is_return", 0)
        dn.ignore_pricing_rule = data.get("ignore_pricing_rule", 0)

        # -------------------------
        # Accounting Dimensions
        # -------------------------
        dn.cost_center = data.get("cost_center")
        dn.project = data.get("project")

        # -------------------------
        # Warehouse
        # -------------------------
        dn.set_warehouse = data.get("set_source_warehouse")

        # -------------------------
        # Items
        # -------------------------
        for row in data.get("items", []):
            dn.append("items", {
                "item_code": row.get("item_code"),
                "qty": row.get("qty"),
                "uom": row.get("uom"),
                "rate": row.get("rate"),
                "warehouse": row.get("warehouse"),
                "sales_order": row.get("sales_order"),
                "so_detail": row.get("so_detail")
            })

        # -------------------------
        # Taxes & Charges
        # -------------------------
        dn.tax_category = data.get("tax_category")
        dn.shipping_rule = data.get("shipping_rule")
        dn.incoterm = data.get("incoterm")
        dn.taxes_and_charges = data.get("sales_taxes_and_charges_template")

        for tax in data.get("taxes", []):
            dn.append("taxes", tax)

        # -------------------------
        # Discount
        # -------------------------
        dn.apply_discount_on = data.get("apply_additional_discount_on")
        dn.additional_discount_percentage = data.get("additional_discount_percentage")
        dn.discount_amount = data.get("additional_discount_amount")

        # -------------------------
        # Address & Contact
        # -------------------------
        dn.billing_address = data.get("billing_address_name")
        dn.shipping_address_name = data.get("shipping_address")
        dn.dispatch_address_name = data.get("dispatch_address_name")
        dn.company_address = data.get("company_address_name")
        dn.contact_person = data.get("contact_person")
        dn.place_of_supply = data.get("place_of_supply")

        # -------------------------
        # Transporter Info
        # -------------------------
        dn.transporter = data.get("transporter")
        dn.mode_of_transport = data.get("mode_of_transport")
        dn.gst_transporter_id = data.get("gst_transporter_id")
        dn.driver = data.get("driver")
        dn.driver_name = data.get("driver_name")
        dn.vehicle_no = data.get("vehicle_no")
        dn.distance = data.get("distance")
        dn.lr_no = data.get("transport_receipt_no")
        dn.lr_date = data.get("transport_receipt_date")

        # -------------------------
        # Sales Partner / Commission
        # -------------------------
        dn.sales_partner = data.get("sales_partner")
        dn.commission_rate = data.get("commission_rate")

        # -------------------------
        # Sales Team
        # -------------------------
        for member in data.get("sales_team", []):
            dn.append("sales_team", member)

        # -------------------------
        # Terms & Printing
        # -------------------------
        dn.terms = data.get("terms")
        dn.letter_head = data.get("letter_head")
        dn.print_heading = data.get("print_heading")
        dn.print_language = data.get("print_language")
        dn.group_same_items = data.get("group_same_items", 0)
        dn.print_without_amount = data.get("print_without_amount", 0)

        # -------------------------
        # Additional Info
        # -------------------------
        dn.source = data.get("source")
        dn.campaign = data.get("campaign")
        dn.territory = data.get("territory")
        dn.instructions = data.get("instructions")

        dn.insert(ignore_permissions=True)
        dn.set_missing_values()
        dn.calculate_taxes_and_totals()
        dn.save()

        return {
            "status": "success",
            "delivery_note": dn.name,
            "message": "Delivery Note Created Successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delivery Note Create API")
        return {"status": "error", "message": str(e)}














@frappe.whitelist()
def list_delivery_notes(
    page=1,
    page_size=10,
    sort_by="modified",
    sort_order="desc",
    search=None,
    status=None,
    customer=None,
    company=None
):
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -------------------------
    # AND FILTERS
    # -------------------------
    filters = {}

    if status:
        filters["status"] = status   # Draft / Submitted / Cancelled

    if customer:
        filters["customer"] = customer

    if company:
        filters["company"] = company

    # -------------------------
    # OR FILTERS (SEARCH)
    # -------------------------
    or_filters = []

    if search:
        or_filters = [
            ["Delivery Note", "name", "like", f"%{search}%"],
            ["Delivery Note", "customer", "like", f"%{search}%"],
            ["Delivery Note", "company", "like", f"%{search}%"],
            ["Delivery Note", "status", "like", f"%{search}%"],
        ]

    # -------------------------
    # DATA QUERY
    # -------------------------
    data = frappe.get_all(
        "Delivery Note",
        fields=[
            "name",
            "posting_date",
            "customer",
            "company",
            "status",
            "grand_total",
            "currency",
            "docstatus",
            "modified"
        ],
        filters=filters,
        or_filters=or_filters,
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # -------------------------
    # TOTAL COUNT (OR-safe)
    # -------------------------
    total = len(
        frappe.get_all(
            "Delivery Note",
            filters=filters,
            or_filters=or_filters,
            pluck="name"
        )
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "status": "success",
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,
        "data": data
    }







@frappe.whitelist(methods=["DELETE", "POST"])
def delete_delivery_note(name):
    """
    Delete Delivery Note (Only Draft allowed)
    """

    try:
        if not name:
            return {
                "status": "error",
                "message": "Delivery Note name is required"
            }

        dn = frappe.get_doc("Delivery Note", name)

        if dn.docstatus != 0:
            return {
                "status": "error",
                "message": "Only Draft Delivery Notes can be deleted"
            }

        frappe.delete_doc(
            "Delivery Note",
            name,
            ignore_permissions=True
        )

        return {
            "status": "success",
            "delivery_note": name,
            "message": "Delivery Note deleted successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delivery Note Delete API")
        return {
            "status": "error",
            "message": str(e)
        }
















# -------------------------------------------------
# HELPER: VALIDATE WAREHOUSE ACCOUNT
# -------------------------------------------------
def validate_warehouse_account(warehouse, company):
    """
    Ensure warehouse has an account mapped for the company
    This prevents: cannot unpack non-iterable NoneType object
    """
    account = frappe.db.get_value(
        "Warehouse",
        warehouse,
        "account"
    )

    if not account:
        frappe.throw(
            f"Warehouse '{warehouse}' has no account mapped for company '{company}'"
        )


# -------------------------------------------------
# UPDATE DELIVERY NOTE API
# -------------------------------------------------
@frappe.whitelist(methods=["PUT", "POST"])
def update_delivery_note(data=None):

    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------
        name = data.get("name")
        if not name:
            return {"status": "error", "message": "Delivery Note name is required"}

        dn = frappe.get_doc("Delivery Note", name)

        if dn.docstatus != 0:
            return {
                "status": "error",
                "message": "Only Draft Delivery Notes can be updated"
            }

        # -------------------------------------------------
        # COMPANY (MUST BE FIRST)
        # -------------------------------------------------
        dn.company = data.get("company") or dn.company
        if not dn.company:
            return {"status": "error", "message": "Company is mandatory"}

        # -------------------------------------------------
        # SELLING PRICE LIST (MANDATORY)
        # -------------------------------------------------
        dn.selling_price_list = data.get("selling_price_list")
        if not dn.selling_price_list:
            return {
                "status": "error",
                "message": "selling_price_list is mandatory"
            }

        dn.price_list_currency = frappe.db.get_value(
            "Price List", dn.selling_price_list, "currency"
        )

        if not dn.price_list_currency:
            return {
                "status": "error",
                "message": "Price List currency not found"
            }

        # -------------------------------------------------
        # BASIC DETAILS
        # -------------------------------------------------
        dn.customer = data.get("customer", dn.customer)
        dn.posting_date = data.get("posting_date") or nowdate()
        dn.posting_time = data.get("posting_time") or nowtime()
        dn.conversion_rate = data.get("conversion_rate") or 1

        # -------------------------------------------------
        # ITEMS (STRICT + VALIDATED)
        # -------------------------------------------------
        if not data.get("items"):
            return {"status": "error", "message": "Items are required"}

        dn.set("items", [])

        for row in data["items"]:
            item_code = row.get("item_code")
            warehouse = row.get("warehouse")

            if not item_code:
                return {"status": "error", "message": "item_code is required"}

            if not warehouse:
                return {
                    "status": "error",
                    "message": f"Warehouse is mandatory for item {item_code}"
                }

            # 🔴 CRITICAL FIX
            validate_warehouse_account(warehouse, dn.company)

            item = frappe.get_doc("Item", item_code)

            dn.append("items", {
                "item_code": item.name,
                "item_name": item.item_name,
                "description": item.description,
                "qty": row.get("qty", 1),
                "rate": row.get("rate", 0),
                "uom": item.stock_uom,
                "stock_uom": item.stock_uom,
                "conversion_factor": 1,
                "warehouse": warehouse,
            })

        # -------------------------------------------------
        # DISCOUNT
        # -------------------------------------------------
        dn.additional_discount_percentage = data.get(
            "additional_discount_percentage", 0
        )

        # -------------------------------------------------
        # TAXES SAFE
        # -------------------------------------------------
        if not dn.taxes:
            dn.set("taxes", [])

        # -------------------------------------------------
        # ERPNext CORE FLOW
        # -------------------------------------------------
        dn.flags.ignore_permissions = True
        dn.set_missing_values()
        dn.calculate_taxes_and_totals()
        dn.save()

        return {
            "status": "success",
            "delivery_note": dn.name,
            "message": "Delivery Note updated successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delivery Note Update API")
        return {"status": "error", "message": str(e)}
