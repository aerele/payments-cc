import frappe
from frappe import _
import json
from frappe.utils import flt
from frappe.query_builder.utils import DocType

@frappe.whitelist(allow_guest=True)
def get_payment_details(order_id):
	default_gateways= frappe.get_all("Default Gateway Account", {
		"parentfield": "default_gateway_accounts",
		"parenttype": "Payment Request",
		"parent": order_id
	},
	[
		"gateway_settings as payment_label",
		"payment_url"
	])
	
	doc= DocType("Payment Request")
	c_doc = c_doc = DocType("Default Gateway Account")    

	gateways = (
		frappe.qb.from_(doc)
		.left_join(c_doc)
		.on(c_doc.parent == doc.name)
		.select(
			doc.name.as_("order_id"),
			doc.grand_total.as_("amount"),
			c_doc.gateway_settings.as_("payment_label"),
			c_doc.payment_url,
			c_doc.icon
		)
		.where(
			(doc.name == order_id) & (doc.show_payments_page == 1) &
			(doc.status.notin(["Paid", "Cancelled"])) &
			(doc.docstatus == 1)
		)
  		.orderby(c_doc.idx)
		.run(as_dict=1)
	)

	for gateway in gateways:
		gateway['payment_label'] = gateway['payment_label'].replace('Settings', '').strip()

	return gateways