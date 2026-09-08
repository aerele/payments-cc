import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import frappe

from payments.templates.pages import payment_success


class TestPaymentSuccess(unittest.TestCase):
	def test_resolves_reference_from_token(self):
		request_local = SimpleNamespace(form_dict=frappe._dict(token="valid-token"))
		cache = Mock()
		cache.get_value.return_value = {
			"doctype": "Payment Request",
			"docname": "PAY-0001",
		}
		doc = Mock()
		doc.get_payment_success_message.return_value = "Payment received"
		context = frappe._dict()

		with (
			patch.object(payment_success.frappe, "local", request_local),
			patch.object(payment_success.frappe, "cache", return_value=cache),
			patch.object(payment_success.frappe, "get_doc", return_value=doc) as get_doc,
		):
			payment_success.get_context(context)

		cache.get_value.assert_called_once_with("payment_success:valid-token")
		get_doc.assert_called_once_with("Payment Request", "PAY-0001")
		self.assertEqual(context.payment_message, "Payment received")

	def test_supports_direct_reference(self):
		frappe.local.form_dict = frappe._dict(
			doctype="Payment Request",
			docname="PAY-0001",
		)
		doc = Mock()
		doc.get_payment_success_message.return_value = "Payment received"
		context = frappe._dict()

		with patch.object(payment_success.frappe, "get_doc", return_value=doc) as get_doc:
			payment_success.get_context(context)

		get_doc.assert_called_once_with("Payment Request", "PAY-0001")
		self.assertEqual(context.payment_message, "Payment received")

	def test_missing_reference_uses_default_message(self):
		frappe.local.form_dict = frappe._dict()
		context = frappe._dict()

		with patch.object(payment_success.frappe, "get_doc") as get_doc:
			payment_success.get_context(context)

		get_doc.assert_not_called()
		self.assertEqual(context.payment_message, "")
