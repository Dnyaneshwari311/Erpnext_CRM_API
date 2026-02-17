__version__ = "0.0.1"


from frappe.desk.form import assign_to


def custom_notify_assignment(*args, **kwargs):
    # STOP default assignment email completely
    return


assign_to.notify_assignment = custom_notify_assignment
