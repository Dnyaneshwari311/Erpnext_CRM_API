import frappe
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error

@frappe.whitelist(methods=["POST"])
def create_item(data=None):
    """
    Create a new Item
    """
    if not data:
        data = frappe.form_dict

    if isinstance(data, str):
        data = frappe.parse_json(data)

    try:
        # Create Item doc
        item = frappe.get_doc({
            "doctype": "Item",
            **data
        })
        item.insert(ignore_permissions=True)  # bypass permission check
        frappe.db.commit()
        return api_response(
            data={"item": item.name},
            message=f"Item {item.name} created",
            status_code=200,
            flatten=True
        )

    except Exception as e:
        return api_error(str(e), 403)








@frappe.whitelist()
def list_items(
    page=1,
    page_size=20,
    sort_by="modified",
    sort_order="desc",
    search=None,
    item_group=None,
    is_stock_item=None,
    price_list="Standard Selling"
):
    """
    List Items with custom part no, rate, amount, search & pagination
    """

    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # -------------------------
    # Build filters
    # -------------------------
    filters = {}
    if item_group:
        filters["item_group"] = item_group
    if is_stock_item is not None:
        filters["is_stock_item"] = 1 if str(is_stock_item).lower() in ("1", "true") else 0

    # -------------------------
    # Search filters
    # -------------------------
    or_filters = []
    if search:
        or_filters = [
            ["item_code", "like", f"%{search}%"],
            ["item_name", "like", f"%{search}%"]
        ]

    # -------------------------
    # Fetch Items
    # -------------------------
    items = frappe.get_all(
        "Item",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=[
            "name",
            "item_code",
            "item_name",
            "item_group",
            "is_stock_item",
            "modified"
        ],
        order_by=f"{sort_by} {sort_order}",
        limit_start=start,
        limit_page_length=page_size
    )

    # -------------------------
    # Fetch Item Prices
    # -------------------------
    item_codes = [i.item_code for i in items]

    prices = frappe.get_all(
        "Item Price",
        filters={
            "item_code": ["in", item_codes],
            "price_list": price_list,
            "selling": 1
        },
        fields=["item_code", "price_list_rate"]
    )

    price_map = {p.item_code: p.price_list_rate for p in prices}

    # -------------------------
    # Attach rate & amount
    # -------------------------
    for item in items:
        rate = price_map.get(item.item_code, 0)
        item.rate = rate
        item.amount = rate  # qty = 1

    # -------------------------
    # Total Count
    # -------------------------
    total = frappe.db.count("Item", filters=filters)

    return api_response(
        data={"item": item.name},
        message=f"Item {item.name} created",
        status_code=200,
        flatten=True
    )






@frappe.whitelist(methods=["PUT", "POST"])
def update_item(data=None):
    """
    Update Item safely
    """
    try:
        if not data:
            data = frappe.form_dict

        if isinstance(data, str):
            data = frappe.parse_json(data)

        name = data.get("name")
        if not name:
            return api_error("Item name is required",400)

        item = frappe.get_doc("Item", name)

        allowed_fields = {
            "item_name",
            "item_group",
            "description",
            "is_stock_item",
            "disabled"
        }

        for field, value in data.items():
            if field in allowed_fields:
                item.set(field, value)

        item.save(ignore_permissions=True)
        frappe.db.commit()

        return api_response(
            data=item.as_dict(),
            message=f"Item {name} updated successfully",
            status_code=200,
            flatten=True
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Item API Error")
        return api_error(str(e), 403)




@frappe.whitelist(methods=["DELETE"])
def delete_item(data=None):
    """
    Delete or Disable Item safely
    """
    try:
        if not data:
            data = frappe.form_dict

        if isinstance(data, str):
            data = frappe.parse_json(data)

        name = data.get("name")
        if not name:
            return api_error("Item name is required",400)

        item = frappe.get_doc("Item", name)

        # Check if item is used in transactions
        linked = (
            frappe.db.exists("Sales Invoice Item", {"item_code": item.item_code}) or
            frappe.db.exists("Delivery Note Item", {"item_code": item.item_code}) or
            frappe.db.exists("Purchase Invoice Item", {"item_code": item.item_code})
        )

        if linked:
            # Soft delete → disable instead
            item.disabled = 1
            item.save(ignore_permissions=True)

            return {
                "status": "success",
                "message": f"Item {name} is linked to transactions and has been disabled instead"
            }

        # Hard delete
        item.delete(ignore_permissions=True)
        frappe.db.commit()

        return api_response(
            data=None,
            message=f"Item {name} deleted successfully",
            status_code=200,
            flatten=True
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Item API Error")
        return api_error(str(e), 403)
