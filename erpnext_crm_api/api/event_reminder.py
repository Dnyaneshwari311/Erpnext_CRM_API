import frappe
from frappe.utils import now_datetime, add_to_date, format_datetime


def send_configurable_event_reminders():
    now = now_datetime()
    print(f"\n=== REMINDER JOB STARTED at {now} ===")

    events = frappe.get_all(
        "Event",
        filters={
            "status": "Open",
            "send_reminder": 1,
            "custom_reminder_sent": 0
        },
        fields=["name", "subject", "starts_on", "owner", "all_day"]
    )

    if not events:
        print("No eligible events found.")
        return

    for event in events:
        print(f"\n>> Checking Event: {event.name}")

        # Get employee reminder minutes (default 15 if not set)
        employee_info = frappe.db.get_value(
            "Employee",
            {"user_id": event.owner},
            ["custom_event_reminder"],
            as_dict=True
        )

        reminder_mins = 60
        if employee_info and employee_info.custom_event_reminder:
            reminder_mins = int(employee_info.custom_event_reminder)

        trigger_time = add_to_date(event.starts_on, minutes=-reminder_mins)

        print("------ TIME DEBUG ------")
        print("NOW:", now)
        print("EVENT START:", event.starts_on)
        print("REMINDER MINS:", reminder_mins)
        print("TRIGGER TIME:", trigger_time)
        print("CONDITION:", trigger_time <= now < event.starts_on)
        print("------------------------")

        # Only send during correct time window
        if not (trigger_time <= now < event.starts_on):
            print("Not in trigger window.")
            continue

        print("Trigger window matched. Collecting participants...")

        participants = frappe.get_all(
            "Event Participants",
            filters={"parent": event.name},
            fields=["email", "reference_doctype", "reference_docname"]
        )

        emails = []

        for p in participants:
            p_email = p.email

            if not p_email:

                if p.reference_doctype == "User":
                    p_email = frappe.db.get_value("User", p.reference_docname, "email")

                elif p.reference_doctype == "Lead":
                    p_email = frappe.db.get_value("Lead", p.reference_docname, "email_id")

                elif p.reference_doctype == "Prospect":
                    contact_name = frappe.db.get_value(
                        "Dynamic Link",
                        {
                            "link_doctype": "Prospect",
                            "link_name": p.reference_docname,
                            "parenttype": "Contact"
                        },
                        "parent"
                    )
                    if contact_name:
                        p_email = frappe.db.get_value("Contact", contact_name, "email_id")

                elif p.reference_doctype == "Employee":
                    emp = frappe.get_doc("Employee", p.reference_docname)
                    p_email = (
                        emp.prefered_email
                        or emp.company_email
                        or emp.personal_email
                        or emp.user_id
                    )

            if p_email:
                emails.append(p_email)

        # Remove duplicates & empty
        emails = list(set(filter(None, emails)))

        print("Final Email List:", emails)

        if not emails:
            print("No valid emails found. Skipping.")
            continue

        # Send reminder
        send_bulk_reminder(event, emails)

        # Mark reminder as sent
        frappe.db.set_value(
            "Event",
            event.name,
            "custom_reminder_sent",
            1,
            update_modified=False
        )

        print(f"Reminder successfully sent for {event.name}")


def send_bulk_reminder(event, recipients):
    time_str = "All Day" if event.all_day else format_datetime(event.starts_on, "hh:mm a")

    frappe.sendmail(
        recipients=recipients,
        subject=f"Reminder: {event.subject}",
        message=f"""
        <p>This is a reminder for the event:</p>
        <p><b>{event.subject}</b></p>
        <p>Starts at: {time_str}</p>
        """,
        reference_doctype="Event",
        reference_name=event.name
    )


def handle_event_reschedule(doc, method):
    if doc.has_value_changed("starts_on"):
        print(f"[HOOK] Event {doc.name} rescheduled.")
        doc.db_set("custom_reminder_sent", 0)
