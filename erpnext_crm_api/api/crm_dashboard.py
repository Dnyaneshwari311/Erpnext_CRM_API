import frappe
from frappe.utils import getdate, nowdate, add_months, sbool

@frappe.whitelist()
def get_crm_dashboard(
    from_date=None,
    to_date=None,
    interval="month",
    company=None,
    sales_person=None
):
    """
    Updated ERPNext Default CRM Dashboard API
    """

    today = getdate(nowdate())

    # Default date range → Last Quarter (ERPNext default)
    if not to_date:
        to_date = today

    if not from_date:
        from_date = add_months(to_date, -3)

    filters = {
        "from_date": from_date,
        "to_date": to_date,
        "company": company,
        "sales_person": sales_person,
        "interval": interval
    }

    return {
        "filters": filters,
        "kpi_cards": get_kpi_cards(filters),
        "charts": {
            "incoming_leads": get_incoming_leads(filters),
            "opportunity_trends": get_opportunity_trends(filters),
            "won_opportunities": get_won_opportunities(filters),
            "territory_opportunity": get_territory_opportunity(filters),
            "campaign_opportunity": get_campaign_opportunity(filters),
            "territory_sales": get_territory_sales(filters),
            "lead_source": get_lead_source(filters)
        }
    }







def get_kpi_cards(filters):
    conditions = []
    values = {}

    if filters.get("company"):
        conditions.append("company = %(company)s")
        values["company"] = filters["company"]

    cond_sql = " AND ".join(conditions)
    cond_sql = f"AND {cond_sql}" if cond_sql else ""

    return {
        "new_leads": frappe.db.sql(
            f"""
            SELECT COUNT(name)
            FROM `tabLead`
            WHERE creation BETWEEN %(from_date)s AND %(to_date)s
            """,
            filters,
        )[0][0],

        "new_opportunities": frappe.db.sql(
            f"""
            SELECT COUNT(name)
            FROM `tabOpportunity`
            WHERE creation BETWEEN %(from_date)s AND %(to_date)s
            {cond_sql}
            """,
            {**filters, **values},
        )[0][0],

        "won_opportunities": frappe.db.sql(
            f"""
            SELECT COUNT(name)
            FROM `tabOpportunity`
            WHERE status = 'Closed'
              AND creation BETWEEN %(from_date)s AND %(to_date)s
            {cond_sql}
            """,
            {**filters, **values},
        )[0][0],

        "open_opportunities": frappe.db.count(
            "Opportunity",
            {
                "status": ["not in", ["Closed", "Lost"]],
                "company": filters.get("company"),
            },
        ),
    }







def get_incoming_leads(filters):
    group_by = get_group_by(filters["interval"])

    return frappe.db.sql(
        f"""
        SELECT
            {group_by} AS label,
            COUNT(name) AS value
        FROM `tabLead`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY label
        ORDER BY MIN(creation)
        """,
        filters,
        as_dict=True,
    )






def get_opportunity_trends(filters):
    group_by = get_group_by(filters["interval"])

    return frappe.db.sql(
        f"""
        SELECT
            {group_by} AS label,
            COUNT(name) AS value
        FROM `tabOpportunity`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY label
        ORDER BY MIN(creation)
        """,
        filters,
        as_dict=True,
    )






def get_won_opportunities(filters):
    return frappe.db.sql(
        """
        SELECT
            DATE_FORMAT(creation, '%%b %%Y') AS label,
            COUNT(name) AS value
        FROM `tabOpportunity`
        WHERE status = 'Closed'
          AND creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY YEAR(creation), MONTH(creation)
        ORDER BY creation
        """,
        filters,
        as_dict=True,
    )






def get_territory_opportunity(filters):
    return frappe.db.sql(
        """
        SELECT territory AS label, COUNT(name) AS value
        FROM `tabOpportunity`
        WHERE territory IS NOT NULL
        GROUP BY territory
        """,
        as_dict=True,
    )





def get_campaign_opportunity(filters):
    return frappe.db.sql(
        """
        SELECT campaign AS label, COUNT(name) AS value
        FROM `tabOpportunity`
        WHERE campaign IS NOT NULL
        GROUP BY campaign
        """,
        as_dict=True,
    )








def get_territory_sales(filters):
    return frappe.db.sql(
        """
        SELECT territory AS label,
               SUM(opportunity_amount) AS value
        FROM `tabOpportunity`
        WHERE status = 'Closed'
        GROUP BY territory
        """,
        as_dict=True,
    )








def get_lead_source(filters):
    return frappe.db.sql(
        """
        SELECT source AS label, COUNT(name) AS value
        FROM `tabLead`
        WHERE source IS NOT NULL
        GROUP BY source
        """,
        as_dict=True,
    )








def get_group_by(interval):
    if interval == "day":
        return "DATE(creation)"
    if interval == "week":
        return "YEARWEEK(creation)"
    return "DATE_FORMAT(creation, '%%b %%Y')"
