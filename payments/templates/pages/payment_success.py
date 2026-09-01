# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe

no_cache = True


def get_context(context):
	doctype = frappe.local.form_dict.get("doctype")
	docname = frappe.local.form_dict.get("docname")

	# BankMuscat flow passes a short-lived token instead of doctype/docname
	token = frappe.local.form_dict.get("token")
	if token and not (doctype and docname):
		cached = frappe.cache().get_value(f"payment_success:{token}")
		if cached:
			doctype = cached.get("doctype")
			docname = cached.get("docname")

	context.payment_message = ""
	if doctype and docname:
		doc = frappe.get_doc(doctype, docname)
		if hasattr(doc, "get_payment_success_message"):
			context.payment_message = doc.get_payment_success_message()
