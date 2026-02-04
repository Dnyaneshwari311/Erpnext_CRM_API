import frappe
from frappe import _
from erpnext_crm_api.api.utils import api_response, api_error


@frappe.whitelist(allow_guest=False)
def get_full_user_list(
    search=None,
    sort_by="full_name",
    sort_order="asc",
    page=1,
    page_size=20
):
    """
    API: Get Full User List with Roles, Search, Sort & Pagination
    Returns only enabled users
    """

    # ---------------------------
    # Pagination
    # ---------------------------
    page = int(page)
    page_size = int(page_size)
    start = (page - 1) * page_size

    # ---------------------------
    # Sorting Validation
    # ---------------------------
    allowed_sort_fields = [
        "full_name",
        "email",
        "username",
        "creation",
        "last_login"
    ]

    if sort_by not in allowed_sort_fields:
        sort_by = "full_name"

    sort_order = "DESC" if sort_order.lower() == "desc" else "ASC"

    # ---------------------------
    # Search Condition
    # ---------------------------
    search_condition = ""
    values = {
        "limit_start": start,
        "page_size": page_size
    }

    if search:
        search_condition = """
            AND (
                u.full_name LIKE %(search)s
                OR u.email LIKE %(search)s
                OR u.username LIKE %(search)s
                OR u.mobile_no LIKE %(search)s
            )
        """
        values["search"] = f"%{search}%"

    # ---------------------------
    # Total Count (SAFE)
    # ---------------------------
    total_count = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabUser` u
        WHERE u.enabled = 1
        {search_condition}
    """.format(search_condition=search_condition), values)[0][0]

    # ---------------------------
    # Fetch Users
    # ---------------------------
    users = frappe.db.sql(f"""
        SELECT
            u.name,
            u.email,
            u.first_name,
            u.last_name,
            u.full_name,
            u.username,
            u.mobile_no,
            u.phone,
            u.location,
            u.user_type,
            u.enabled,
            u.time_zone,
            u.language,
            u.last_login,
            u.creation,
            u.modified
        FROM `tabUser` u
        WHERE u.enabled = 1
        {search_condition}
        ORDER BY u.{sort_by} {sort_order}
        LIMIT %(limit_start)s, %(page_size)s
    """, values, as_dict=True)

    # ---------------------------
    # Fetch Roles per User
    # ---------------------------
    for user in users:
        user["roles"] = frappe.get_all(
            "Has Role",
            filters={"parent": user["name"]},
            pluck="role"
        )
    return api_response(
        data={
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "data": users
        },
        message=_("User List Fetched Successfully"),
        status_code=200,
        flatten=True
    )