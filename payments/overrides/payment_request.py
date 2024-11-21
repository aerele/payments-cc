import frappe
from erpnext.accounts.doctype.payment_request.payment_request import (
	PaymentRequest, get_gateway_details, _get_payment_gateway_controller
)
from frappe.utils import flt
from frappe import _
from frappe import bold


class CustomPaymentRequest(PaymentRequest):
	def validate(self):
		if self.show_payments_page:
			#clear payment gateway details
			self.payment_gateway_account = ""
			self.payment_gateway = ""
			self.payment_account = ""
			self.payment_channel = ""
			if frappe.get_doc("Payment Gateway Settings").show_url_in_draft_state:
				self.set_payment_page_url()
		else:
			self.payment_gateway_account = frappe.get_value(
				"Payment Gateway Account",
				{"is_default": 1, "company": self.company},
				"name"
			)
		super().validate()
		self.validate_payment_gateway_account()

	def validate_payment_gateway_account(self):
		if self.payment_gateway_account:
			if self.company != frappe.get_value("Payment Gateway Account", self.payment_gateway_account, "company"):
				frappe.throw(_(f"Payment Gateway Account({bold(self.payment_gateway_account)}) does not belong to the company {bold(self.company)}"))

	def on_submit(self):
		if self.payment_request_type == "Outward":
			self.db_set("status", "Initiated")
			return

		elif self.payment_request_type == "Inward":
			self.db_set("status", "Requested")

		if not self.show_payments_page:
			super().on_submit()

	def before_submit(self):
		super().before_submit()
		self.default_gateway_accounts = []
		if self.show_payments_page:
			self.set_payment_page_url()

	def set_payment_page_url(self):
		gateways = frappe.get_doc("Payment Gateway Settings").get_default_gateways(self.company)
		for gateway in gateways:
			payment_url = self.get_payment_url(gateway.get("payment_gateway"))
			gateway.update({
				"payment_url": payment_url
			})
			self.append("default_gateway_accounts", gateway)

	def set_as_failed(self):
		self.db_set("status", "Failed")
		if self.docstatus == 1:
			self.db_set("docstatus", 2)


	def get_payment_url(self, payment_gateway= None):

		if not self.show_payments_page:
			return super().get_payment_url()

		if self.reference_doctype != "Fees":
			data = frappe.db.get_value(
				self.reference_doctype, self.reference_name, ["company", "customer_name"], as_dict=1
			)
		else:
			data = frappe.db.get_value(
				self.reference_doctype, self.reference_name, ["student_name"], as_dict=1
			)
			data.update({"company": frappe.defaults.get_defaults().company})

		if not payment_gateway: return

		controller = _get_payment_gateway_controller(payment_gateway)
		controller.validate_transaction_currency(self.currency)

		if hasattr(controller, "validate_minimum_transaction_amount"):
			controller.validate_minimum_transaction_amount(self.currency, self.grand_total)

		if hasattr(controller, "get_payment_page_url"):
			return controller.get_payment_page_url(
				**{
					"amount": flt(self.grand_total, self.precision("grand_total")),
					"title": data.company,
					"description": self.subject,
					"reference_doctype": "Payment Request",
					"reference_docname": self.name,
					"payer_email": self.email_to or frappe.session.user,
					"payer_name": data.customer_name,
					"order_id": self.name,
					"currency": self.currency,
				}
			)
		else:
			frappe.log_error(
				f"Payment Page URL Option Not Implemented in {controller.name}"
			)