# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe import bold

class PaymentGatewaySettings(Document):
	def get_default_gateways(self, company=None):
		if not company:
			frappe.throw("Company is mandatory for getting default gateways")

		controllers = []
		if self.default_gateways:
			return [{
				"company": gateway.company,
				"gateway_settings": gateway.gateway_settings,
				"payment_gateway": gateway.payment_gateway,
				"payment_gateway_account": gateway.payment_gateway_account,
				"icon": gateway.icon
			} for gateway in self.default_gateways if gateway.company == company]


def create_payment_gateway_name(self, method):
	if not self.company:
		self.company = frappe.get_cached_value("Global Defaults", "Global Defaults", "default_company")

	company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
	self.name = self.payment_gateway + " - " + self.currency +" - "+ company_abbr

def validate_payment_gateway_account(self, method):
	if self.company != frappe.get_value("Account", self.payment_account, "company"):
		frappe.throw(_(f"Payment Account({bold(self.payment_account)}) does not belong to the company {bold(self.company)}"))