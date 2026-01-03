import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def create_sales_invoice(data=None):
    """
    Create a Sales Invoice following ERPNext flow.
    `data` should be JSON with parent + items fields.
    """
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    # Create new Sales Invoice doc
    try:
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            **data
        })
        si.insert(ignore_permissions=True)
        si.submit() if data.get("submit") else None  # optional submit
        return {"status": "success", 
                "status_code":201,
                "message":"Sales Invoice Created Successfully ",
                "sales_invoice": si.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}











@frappe.whitelist()
def list_sales_invoices(
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
        # For Sales Invoice, status can be "Draft", "Submitted", "Cancelled"
        filters["docstatus"] = {"Draft": 0, "Submitted": 1, "Cancelled": 2}.get(status, None)
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
            ["Sales Invoice", "name", "like", f"%{search}%"],
            ["Sales Invoice", "customer", "like", f"%{search}%"],
            ["Sales Invoice", "company", "like", f"%{search}%"],
            ["Sales Invoice", "currency", "like", f"%{search}%"],
        ]

    # -------------------------
    # DATA QUERY
    # -------------------------
    data = frappe.get_all(
        "Sales Invoice",
        fields=[
            "name",
            "posting_date",
            "due_date",
            "customer",
            "company",
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
            "Sales Invoice",
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











@frappe.whitelist(methods=["POST"])
def update_sales_invoice(name=None, data=None):
    """
    Update Sales Invoice via API (SAFE)
    """

    # Frappe sends everything in form_dict
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    # Accept name from URL OR body
    name = name or data.get("name")

    if not name:
        frappe.throw("Sales Invoice name is required")

    try:
        si = frappe.get_doc("Sales Invoice", name)

        was_submitted = si.docstatus == 1
        if was_submitted:
            si.cancel()

        # -------------------------
        # UPDATE FIELDS
        # -------------------------
        si.customer = data.get("customer", si.customer)
        si.company = data.get("company", si.company)
        si.posting_date = data.get("date", si.posting_date)
        si.currency = data.get("currency", si.currency)
        si.selling_price_list = data.get("price_list", si.selling_price_list)
        si.conversion_rate = data.get("exchange_rate", si.conversion_rate)

        # -------------------------
        # UPDATE ITEMS
        # -------------------------
        if "items" in data:
            si.items = []
            for item in data.get("items", []):
                si.append("items", {
                    "item_code": item.get("item_code"),
                    "qty": item.get("qty"),
                    "rate": item.get("rate"),
                    "delivery_date": item.get("delivery_date")
                })

        si.save(ignore_permissions=True)

        if was_submitted or data.get("submit"):
            si.submit()

        return {
            "status": "success",
            "status_code":200,
            "sales_invoice": si.name,
            "message":"sales invoice updated successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Sales Invoice API")
        return {
            "status": "error",
            "message": str(e)
        }








@frappe.whitelist(methods=["DELETE"])
def delete_sales_invoice(name):
    """
    Delete Sales Invoice
    """
    try:
        si = frappe.get_doc("Sales Invoice", name)
        # Cancel if submitted
        if si.docstatus == 1:
            si.cancel()
        si.delete()
        return {"status": "success", "message": f"Sales Invoice {name} deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist(methods=["DELETE"])
def delete_sales_invoice(name=None):
    """
    Delete Sales Invoice
    """

    # Frappe sends params via form_dict
    name = name or frappe.form_dict.get("name")

    if not name:
        frappe.throw("Sales Invoice name is required")

    try:
        si = frappe.get_doc("Sales Invoice", name)

        # Cancel if submitted
        if si.docstatus == 1:
            si.cancel()

        si.delete(ignore_permissions=True)

        return {
            "status": "success",
            "status_code":200,
            "message": f"Sales Invoice {name} deleted"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Sales Invoice API")
        return {
            "status": "error",
            "message": str(e)
        }











_

@frappe.whitelist()
def get_sales_invoice_by_id(name=None):
    """
    Get Sales Invoice by ID (name)
    """

    # Accept name from URL or body
    name = name or frappe.form_dict.get("name")

    if not name:
        frappe.throw(_("Sales Invoice name is required"))

    try:
        si = frappe.get_doc("Sales Invoice", name)

        return {
            "status": "success",
            "status_code": 200,
            "message":"Sales Invoice Fetched Successfully ",
            "data": {
                "name": si.name,
                "posting_date": si.posting_date,
                "due_date": si.due_date,
                "customer": si.customer,
                "company": si.company,
                "currency": si.currency,
                "grand_total": si.grand_total,
                "net_total": si.net_total,
                "status": si.status,
                "docstatus": si.docstatus,
                "items": [
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "qty": item.qty,
                        "rate": item.rate,
                        "amount": item.amount,
                        "warehouse": item.warehouse
                    }
                    for item in si.items
                ]
            }
        }

    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "status_code": 404,
            "message": "Sales Invoice not found"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Sales Invoice API")
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }
















