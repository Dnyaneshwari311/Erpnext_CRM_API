import frappe
@frappe.whitelist(allow_guest=False)
def get_full_user_list():
    """
    Returns full user details with roles
    """

    users = frappe.db.sql("""
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
        ORDER BY u.full_name
    """, as_dict=True)

    # Fetch roles per user
    for user in users:
        user["roles"] = frappe.get_all(
            "Has Role",
            filters={"parent": user["name"]},
            pluck="role"
        )

    return {
        "status": "success",
         "message":"User List Fetched Successfully",
        "count": len(users),
        "data": users
    }
