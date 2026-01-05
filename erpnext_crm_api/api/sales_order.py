import frappe

@frappe.whitelist(methods=["POST"])
def create_sales_order(data=None):
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        so = frappe.new_doc("Sales Order")

        # 🔹 BASIC FIELDS
        so.customer = data.get("customer")
        so.transaction_date = data.get("date")
        so.delivery_date = data.get("delivery_date")
        so.company = data.get("company")
        so.order_type = data.get("order_type")
        so.currency = data.get("currency")
        so.price_list = data.get("price_list")
        so.exchange_rate = data.get("exchange_rate", 1)
        so.customer_purchase_order = data.get("customer_purchase_order")

        # 🔹 ACCOUNTING DIMENSIONS
        so.cost_center = data.get("cost_center")
        so.project = data.get("project")

        # 🔹 FLAGS
        so.ignore_pricing_rule = data.get("ignore_pricing_rule", 0)

        # 🔹 ITEMS
        for row in data.get("items", []):
            so.append("items", {
                "item_code": row.get("item_code"),
                "qty": row.get("qty"),
                "rate": row.get("rate"),
                "delivery_date": row.get("delivery_date"),
                "warehouse": row.get("warehouse")
            })

        # 🔹 TAXES
        for tax in data.get("taxes", []):
            so.append("taxes", {
                "charge_type": tax.get("charge_type"),
                "account_head": tax.get("account_head"),
                "rate": tax.get("rate")
            })

        # 🔹 PAYMENT SCHEDULE
        for p in data.get("payment_schedule", []):
            so.append("payment_schedule", {
                "payment_term": p.get("payment_term"),
                "due_date": p.get("due_date"),
                "invoice_portion": p.get("invoice_portion"),
                "payment_amount": p.get("payment_amount")
            })

        # 🔹 SALES TEAM
        for s in data.get("sales_team", []):
            so.append("sales_team", {
                "sales_person": s.get("sales_person"),
                "allocated_percentage": s.get("allocated_percentage"),
                "commission_rate": s.get("commission_rate")
            })

        # 🔹 ADDITIONAL INFO
        so.source = data.get("source")
        so.campaign = data.get("campaign")
        so.territory = data.get("territory")

        so.insert(ignore_permissions=True)

        return {
            "status": "success",
            "status_code":201,
            "message": "Sales Order created",
            "sales_order": so.name,
            # "docstatus": so.docstatus
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sales Order Create Error")
        return {"status": "error", "message": str(e)}















@frappe.whitelist(methods=["PUT", "POST"])
def update_sales_order(data=None):
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        so = frappe.get_doc("Sales Order", data.get("name"))

        if so.docstatus != 0:
            return {
                "status": "error",
                "message": "Only Draft Sales Orders can be updated"
            }

        # 🔹 UPDATE BASIC FIELDS
        for field in [
            "customer", "delivery_date", "order_type",
            "currency", "price_list", "exchange_rate",
            "cost_center", "project"
        ]:
            if field in data:
                so.set(field, data.get(field))

        # 🔹 RESET & RE-ADD ITEMS
        if "items" in data:
            so.set("items", [])
            for row in data["items"]:
                so.append("items", row)

        # 🔹 RESET & RE-ADD TAXES
        if "taxes" in data:
            so.set("taxes", [])
            for tax in data["taxes"]:
                so.append("taxes", tax)

        so.save(ignore_permissions=True)

        return {
            "status": "success",
            "status_code":200,
            "message": "Sales Order updated",
            "sales_order": so.name
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}






@frappe.whitelist()
def list_sales_orders(
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
        filters["status"] = status

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
            ["Sales Order", "name", "like", f"%{search}%"],
            ["Sales Order", "customer", "like", f"%{search}%"],
            ["Sales Order", "company", "like", f"%{search}%"],
            ["Sales Order", "status", "like", f"%{search}%"],
        ]

    # -------------------------
    # DATA QUERY
    # -------------------------
    data = frappe.get_all(
        "Sales Order",
        fields=[
            "name",
            "transaction_date",
            "delivery_date",
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
            "Sales Order",
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









@frappe.whitelist(methods=["DELETE"])
def delete_sales_order(name):
    """
    Delete Sales Order
    - Draft: Direct delete
    - Submitted: Cancel → Delete
    - Cancelled: Delete
    """
    try:
        if not name:
            return {
                "status": "error",
                "message": "Sales Order name is required"
            }

        so = frappe.get_doc("Sales Order", name)

        # 🔹 If Submitted → Cancel first
        if so.docstatus == 1:
            so.cancel()

        # 🔹 Delete (Draft or Cancelled)
        so.delete(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "status_code":200,
            "message": f"Sales Order {name} deleted successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sales Order Delete Error")
        return {
            "status": "error",
            "message": str(e)
        }








@frappe.whitelist()
def cancel_sales_order(name):
    so = frappe.get_doc("Sales Order", name)

    if so.docstatus != 1:
        frappe.throw("Only Submitted Sales Orders can be cancelled")

    so.cancel()

    return {
        "status": "success",
        "sales_order": so.name,
        "docstatus": so.docstatus
    }








@frappe.whitelist(methods=["GET"])
def get_sales_order_by_id(name):
    """
    Get Sales Order details by ID (name)
    """
    try:
        if not name:
            return {
                "status": "error",
                "message": "Sales Order name is required"
            }

        so = frappe.get_doc("Sales Order", name)

        return {
            "status": "success",
            "message":"Sales Order Fetched Successfully",
            "data": {
                # 🔹 BASIC INFO
                "name": so.name,
                "customer": so.customer,
                "transaction_date": so.transaction_date,
                "delivery_date": so.delivery_date,
                "company": so.company,
                "order_type": so.order_type,
                "status": so.status,
                "currency": so.currency,
                "price_list": so.selling_price_list,

                "exchange_rate": so.conversion_rate,
                "customer_purchase_order": so.po_no,
                # 🔹 TOTALS
                "total": so.total,
                "total_taxes_and_charges": so.total_taxes_and_charges,
                "grand_total": so.grand_total,

                # 🔹 ACCOUNTING DIMENSIONS
                "cost_center": so.cost_center,
                "project": so.project,

                # 🔹 ITEMS
                "items": [
                    {
                        "item_code": i.item_code,
                        "item_name": i.item_name,
                        "qty": i.qty,
                        "rate": i.rate,
                        "amount": i.amount,
                        "delivery_date": i.delivery_date,
                        "warehouse": i.warehouse
                    }
                    for i in so.items
                ],

                # 🔹 TAXES
                "taxes": [
                    {
                        "charge_type": t.charge_type,
                        "account_head": t.account_head,
                        "rate": t.rate,
                        "tax_amount": t.tax_amount,
                        "total": t.total
                    }
                    for t in so.taxes
                ],

                # 🔹 PAYMENT SCHEDULE
                "payment_schedule": [
                    {
                        "payment_term": p.payment_term,
                        "due_date": p.due_date,
                        "invoice_portion": p.invoice_portion,
                        "payment_amount": p.payment_amount
                    }
                    for p in so.payment_schedule
                ],

                # 🔹 SALES TEAM
                "sales_team": [
                    {
                        "sales_person": s.sales_person,
                        "allocated_percentage": s.allocated_percentage,
                        "commission_rate": s.commission_rate
                    }
                    for s in so.sales_team
                ],

                # 🔹 META
                "docstatus": so.docstatus,
                "created_on": so.creation,
                "modified_on": so.modified
            }
        }

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": "Sales Order not found"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Sales Order Error")
        return {
            "status": "error",
            "message": str(e)
        }











from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice


@frappe.whitelist(methods=["POST"])
def create_sales_invoice_from_sales_order(data=None):
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    sales_order = data.get("sales_order")

    if not sales_order:
        return {
            "status": "error",
            "message": "sales_order is required"
        }

    try:
        # 🔹 Validate Sales Order
        so = frappe.get_doc("Sales Order", sales_order)

        if so.docstatus != 1:
            return {
                "status": "error",
                "message": "Sales Order must be Submitted to create Sales Invoice"
            }

        # 🔹 Create Sales Invoice using ERPNext mapper
        si = make_sales_invoice(sales_order)

        # 🔹 Optional overrides
        if data.get("posting_date"):
            si.posting_date = data.get("posting_date")

        if data.get("due_date"):
            si.due_date = data.get("due_date")

        if data.get("remarks"):
            si.remarks = data.get("remarks")

        # 🔹 Insert Invoice
        si.insert(ignore_permissions=True)

        # 🔹 Optional auto-submit
        if data.get("submit"):
            si.submit()

        return {
            "status": "success",
            "status_code": 201,
            "message": "Sales Invoice created successfully",
            "sales_invoice": si.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Sales Invoice Error")
        return {
            "status": "error",
            "message": str(e)
        }







import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
from erpnext.stock.utils import get_latest_stock_qty


@frappe.whitelist(methods=["POST"])
def create_delivery_note_from_sales_order(data=None):
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    sales_order = data.get("sales_order")

    if not sales_order:
        return {
            "status": "error",
            "message": "sales_order is required"
        }

    try:
        # 🔹 Validate Sales Order
        so = frappe.get_doc("Sales Order", sales_order)

        if so.docstatus != 1:
            return {
                "status": "error",
                "message": "Sales Order must be Submitted"
            }

        # 🔹 Create DN draft (no DB insert yet)
        dn = make_delivery_note(sales_order)

        # 🔹 Optional warehouse override
        if data.get("warehouse"):
            for item in dn.items:
                item.warehouse = data.get("warehouse")

        # 🔹 STOCK PRE-CHECK (IMPORTANT)
        for item in dn.items:
            available_qty = get_latest_stock_qty(
                item.item_code,
                item.warehouse
            )

            if available_qty < item.qty:
                return {
                    "status": "error",
                    "message": (
                        f"Insufficient stock for {item.item_code} "
                        f"in {item.warehouse}. "
                        f"Available: {available_qty}, "
                        f"Required: {item.qty}"
                    )
                }

        # 🔹 Insert DN
        dn.insert(ignore_permissions=True)

        # 🔹 Auto-submit
        if data.get("submit"):
            dn.submit()

        return {
            "status": "success",
            "status_code": 201,
            "message": "Delivery Note created successfully",
            "delivery_note": dn.name,
            "docstatus": dn.docstatus
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delivery Note API Error")
        return {
            "status": "error",
            "message": str(e)
        }







@frappe.whitelist(methods=["POST"])
def submit_sales_order(name=None):
    """
    Submit a Draft Sales Order
    """
    try:
        if not name:
            return {
                "status": "error",
                "message": "Sales Order name is required"
            }

        # Fetch the Sales Order
        so = frappe.get_doc("Sales Order", name)

        # Only Draft orders can be submitted
        if so.docstatus != 0:
            return {
                "status": "error",
                "message": f"Only Draft Sales Orders can be submitted (Current docstatus: {so.docstatus})"
            }

        # Submit the Sales Order
        so.submit()

        return {
            "status": "success",
            "status_code": 200,
            "message": f"Sales Order {name} submitted successfully",
            "sales_order": so.name,
        
        }

    except frappe.ValidationError as ve:
        return {
            "status": "error",
            "message": str(ve)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Submit Sales Order Error")
        return {
            "status": "error",
            "message": str(e)
        }
