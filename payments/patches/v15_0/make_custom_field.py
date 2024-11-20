import frappe
from payments.utils.utils import create_default_gateway_account_fields

def execute():
	create_default_gateway_account_fields()