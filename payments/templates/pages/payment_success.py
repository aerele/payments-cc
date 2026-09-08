# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe

no_cache = True


def get_context(context):
	context.payment_message = ""
	doctype, docname = get_payment_reference()
	if not (doctype and docname):
		return

	doc = frappe.get_doc(doctype, docname)
	if hasattr(doc, "get_payment_success_message"):
		context.payment_message = doc.get_payment_success_message()


def get_payment_reference():
	form_dict = frappe.local.form_dict
	token = form_dict.get("token")

	if token:
		reference = frappe.cache().get_value(f"payment_success:{token}") or {}
		return reference.get("doctype"), reference.get("docname")

	return form_dict.get("doctype"), form_dict.get("docname")
