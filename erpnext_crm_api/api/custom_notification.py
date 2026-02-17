# import frappe


# def handle_assignment_email(doc, method):
#     """
#     Stop default assignment email.
#     Send simple plain email instead.
#     """

#     # Only for assignment (not other todos)
#     if not doc.reference_type or not doc.reference_name:
#         return

#     user_email = frappe.db.get_value("User", doc.allocated_to, "email")

#     if not user_email:
#         return

#     # ✅ Send simple plain email
#     frappe.sendmail(
#         recipients=[user_email],
#         subject=f"New Assignment: {doc.reference_type} {doc.reference_name}",
#         message=f"""
# Hello,

# You have been assigned a task.

# Document: {doc.reference_type} - {doc.reference_name}

# Please check ERP system.

# Thank you.
# """,
#         delayed=False
#     )

#     # ❌ Delete system notification email queue
#     frappe.db.delete("Email Queue", {
#         "reference_name": doc.reference_name,
#         "status": ("in", ["Not Sent", "Sending"])
#     })








import frappe
from frappe import _
from frappe.utils import nowdate,get_datetime, format_datetime
from erpnext_crm_api.api.utils import api_response, api_error, get_paginated_data


def handle_assignment_email(doc, method):
    """
    Stop default assignment email.
    Send simple custom reminder style email instead.
    """

    # Only proceed if assignment is linked to a document
    if not doc.reference_type or not doc.reference_name:
        return

    # Only customize for Event
    if doc.reference_type != "Event":
        return

    # Get Event document
    event = frappe.get_doc("Event", doc.reference_name)

    user_email = frappe.db.get_value("User", doc.allocated_to, "email")

    if not user_email:
        return

    # Format event start time
    start_time = format_datetime(event.starts_on)

    # ✅ Send custom simple email
    frappe.sendmail(
        recipients=[user_email],
        subject=f"Reminder for Event: {event.subject}",
        message=f"""
Hello,

This is a reminder for the event: {event.subject}

Starts at: {start_time}

Thank you.
""",
        delayed=False
    )

    # ❌ Remove default queued email
    frappe.db.delete("Email Queue", {
        "reference_name": doc.reference_name,
        "status": ("in", ["Not Sent", "Sending"])
    })









@frappe.whitelist(allow_guest=True)

def send_event_assignment_email(todo=None):
    """
    API to send custom assignment email for Event ToDo
    """

    if not todo:
        frappe.throw("ToDo ID is required")

    doc = frappe.get_doc("ToDo", todo)

    # Only for Event assignment
    if doc.reference_type != "Event":
        return {"status": "ignored", "reason": "Not an Event assignment"}

    if not doc.reference_name:
        return {"status": "ignored", "reason": "No reference"}

    event = frappe.get_doc("Event", doc.reference_name)

    user_email = frappe.db.get_value("User", doc.allocated_to, "email")

    if not user_email:
        return {"status": "ignored", "reason": "User email not found"}

    start_time = format_datetime(event.starts_on)

    frappe.sendmail(
        recipients=[user_email],
        subject=f"Reminder for Event: {event.subject}",
        message=f"""
Hello,

This is a reminder for the event: {event.subject}

Starts at: {start_time}

Thank you.
""",
        delayed=False
    )

    return {
        "status": "success",
        "message": "Custom assignment email sent",
        "event": event.name,
        "user": doc.allocated_to
    }






# @frappe.whitelist(allow_guest=False)
# def get_event_assignments(
#     search=None,
#     page=1,
#     page_size=20,
#     sort_by="creation",
#     sort_order="desc"
# ):
#     """
#     Paginated Event assignment list (Today + Upcoming only)
#     """

#     try:
#         today = nowdate()

#         # Step 1: get today & upcoming events
#         event_names = frappe.get_all(
#             "Event",
#             filters={
#                 "starts_on": [">=", today]
#             },
#             pluck="name"
#         )

#         if not event_names:
#             return api_response(
#                 data={
#                     "page": int(page),
#                     "page_size": int(page_size),
#                     "total_records": 0,
#                     "total_pages": 0,
#                     "data": []
#                 },
#                 message=_("No upcoming events found")
#             )

#         # Step 2: get ToDo only for those events
#         result = get_paginated_data(
#             doctype="ToDo",
#             fields=[
#                 "name",
#                 "reference_name",
#                 "allocated_to",
#                 "status",
#                 "creation"
#             ],
#             filters={
#                 "reference_type": "Event",
#                 "reference_name": ["in", event_names]
#             },
#             search=search,
#             search_fields=["reference_name", "allocated_to"],
#             sort_by=sort_by,
#             sort_order=sort_order,
#             page=page,
#             page_size=page_size
#         )

#         data = []

#         for row in result["results"]:
#             event = frappe.db.get_value(
#                 "Event",
#                 row["reference_name"],
#                 ["subject", "starts_on"],
#                 as_dict=True
#             )

#             data.append({
#                 "todo": row["name"],
#                 "event": row["reference_name"],
#                 "event_subject": event.subject if event else None,
#                 "starts_on": format_datetime(event.starts_on) if event else None,
#                 "assigned_to": row["allocated_to"],
#                 "status": row["status"]
#             })

#         return api_response(
#     data={
#         "page": int(page),
#         "page_size": int(page_size),
#         "total_records": result["count"],
#         "total_pages": result["total_pages"],
#         "data": data
#     },
#     message=_("Event Assignment List Fetched Successfully")
# )



#     except PermissionError:
#         return api_error("Not permitted", 403)

#     except Exception as e:
#         return api_error(str(e), 500)





@frappe.whitelist(allow_guest=False)
def get_event_assignments(
    search=None,
    page=1,
    page_size=20,
    sort_by="creation",
    sort_order="desc",
    filter_type=None  # 'today' or 'upcoming'
):
    """
    Paginated Event assignment list.

    filter_type:
        - None: fetch all events
        - 'today': fetch events starting today only
        - 'upcoming': fetch events starting after today
    """
    try:
        today = nowdate()  # YYYY-MM-DD

        # Step 1: build filters based on filter_type
        event_filters = {}
        if filter_type == "today":
            # get events starting anytime today
            event_filters["starts_on"] = ["between", [today + " 00:00:00", today + " 23:59:59"]]
        elif filter_type == "upcoming":
            # get events starting after today
            event_filters["starts_on"] = [">", today + " 23:59:59"]

        # Step 2: get event names
        event_names = frappe.get_all(
            "Event",
            filters=event_filters,
            pluck="name"
        )

        if not event_names:
            return api_response(
                data={
                    "page": int(page),
                    "page_size": int(page_size),
                    "total_records": 0,
                    "total_pages": 0,
                    "data": []
                },
                message=_("No events found")
            )

        # Step 3: get ToDo only for those events
        result = get_paginated_data(
            doctype="ToDo",
            fields=[
                "name",
                "reference_name",
                "allocated_to",
                "status",
                "creation"
            ],
            filters={
                "reference_type": "Event",
                "reference_name": ["in", event_names]
            },
            search=search,
            search_fields=["reference_name", "allocated_to"],
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )

        data = []

        for row in result["results"]:
            event = frappe.db.get_value(
                "Event",
                row["reference_name"],
                ["subject", "starts_on"],
                as_dict=True
            )

            data.append({
                "todo": row["name"],
                "event": row["reference_name"],
                "event_subject": event.subject if event else None,
                "starts_on": format_datetime(event.starts_on) if event else None,
                "assigned_to": row["allocated_to"],
                "status": row["status"]
            })

        return api_response(
            data={
                "page": int(page),
                "page_size": int(page_size),
                "total_records": result["count"],
                "total_pages": result["total_pages"],
                "data": data
            },
            message=_("Event Assignment List Fetched Successfully")
        )

    except PermissionError:
        return api_error("Not permitted", 403)

    except Exception as e:
        return api_error(str(e), 500)






@frappe.whitelist(allow_guest=False)
def create_event_from_lead(
    lead,
    subject,
    starts_on,
    ends_on=None,
    assigned_to=None,
    description=None
):
    """
    Create Event linked to Lead and optionally assign user
        - If assigned_to is provided, creates a ToDo and sends custom assignment email
        - Returns created Event and ToDo details
        - Required: lead, subject, starts_on
        - Optional: ends_on, assigned_to, description
        - Permission: User must have permission to create Event and ToDo
        - Errors: 400 for missing fields, 404 for invalid Lead, 403 for permission issues
    """

    try:
        if not lead or not subject or not starts_on:
            return api_error("lead, subject, starts_on required", 400)

        if not frappe.db.exists("Lead", lead):
            return api_error("Lead not found", 404)

        # Create Event
        event = frappe.get_doc({
            "doctype": "Event",
            "subject": subject,
            "starts_on": get_datetime(starts_on),
            "ends_on": get_datetime(ends_on) if ends_on else None,
            "description": description,
            "event_type": "Private",
            "reference_doctype": "Lead",
            "reference_docname": lead
        })
        event.insert(ignore_permissions=True)

        todo_name = None

        # Optional assignment
        if assigned_to:
            todo = frappe.get_doc({
                "doctype": "ToDo",
                "allocated_to": assigned_to,
                "reference_type": "Event",
                "reference_name": event.name,
                "description": subject
            })
            todo.insert(ignore_permissions=True)
            todo_name = todo.name

            # send assignment email
            try:
                from erpnext_crm_api.api.custom_notification import send_event_assignment_email
                send_event_assignment_email(todo.name)
            except Exception:
                pass

        return api_response(
            data={
                "event": event.name,
                "lead": lead,
                "subject": subject,
                "starts_on": event.starts_on,
                "assigned_to": assigned_to,
                "todo": todo_name
            },
            message=_("Event Created Successfully from Lead")
        )

    except PermissionError:
        return api_error("Not permitted", 403)

    except Exception as e:
        return api_error(str(e), 500)
