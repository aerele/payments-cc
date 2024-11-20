# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentGatewaySettings(Document):
	def get_default_gateways(self):
		controllers = []
		if self.default_gateways:
			return [{
				"gateway_settings": gateway.gateway_settings,
				"payment_gateway": gateway.payment_gateway,
				"payment_gateway_account": gateway.payment_gateway_account,
				"icon": gateway.icon
			} for gateway in self.default_gateways]
