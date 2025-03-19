# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import binascii
import hashlib
from string import Template

import frappe
from Crypto.Cipher import AES
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document
from frappe.utils import call_hook_method, cstr, get_url

from payments.utils import create_payment_gateway


class CCAvenueSettings(Document):
	supported_currencies = ("INR", "USD", "SGD", "GBP", "EUR")

	iv = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"

	def get_payment_page_url(self, **kwargs):
		return self.get_gateway_url(template=False, **kwargs)

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(
				frappe._(
					"Please select another payment method. CCAvenue does not support transactions in currency '{0}'"
				).format(currency)
			)

	def on_update(self):
		create_payment_gateway(
			"CCAvenue-" + self.merchant_id,
			settings="CCAvenue Settings",
			controller=self.merchant_id,
		)
		call_hook_method("payment_gateway_enabled", gateway="CCAvenue-" + self.merchant_id)

	def get_payment_url(self, **kwargs):
		frappe.log_error("data: ", kwargs)
		self.order_id = create_request_log(
			kwargs, service_name="CCAvenue", name=kwargs.get("order_id", "")
		).name
		return get_url(f"ccavenue_checkout?order_id={self.order_id}")

	@frappe.whitelist()
	def get_iframe_template(self, **kwargs):
		return self.get_gateway_url(template=False, **kwargs)

	def get_gateway_url(self, template=False, **kwargs):
		self.validate_mandatory_values(**kwargs)
		encrypted_req = self.get_encrypted_request(**kwargs)

		gateway_domain = "https://secure.ccavenue.com"
		if self.use_sandbox:
			gateway_domain = "https://test.ccavenue.com"

		iframe = f"""
		<iframe
			width="482" height="500" scrolling="No" frameborder="0"  id="paymentFrame"
			src="{gateway_domain}/transaction/transaction.do?command=initiateTransaction&merchant_id=$mid&encRequest=$encReq&access_code=$xscode">
	  	</iframe>
		"""

		formated_template = Template(iframe).safe_substitute(
			mid=self.merchant_id, encReq=encrypted_req, xscode=self.get_password("access_code")
		)
		if template:
			return formated_template

		from bs4 import BeautifulSoup

		return BeautifulSoup(formated_template, "html.parser").find("iframe")["src"]

	def get_encrypted_request(self, **kwargs):
		merchant_data = self.get_merchant_data(**kwargs)

		return self.encrypt(merchant_data, self.get_password("working_key"))

	def get_merchant_data(self, **kwargs):
		self.redirect_url = get_url(
			"api/method/payments.templates.pages.ccavenue_checkout.verify_payment_status"
		)
		self.cancel_url = get_url("api/method/payments.templates.pages.ccavenue_checkout.cancel_payment")

		merchant_id = kwargs.get("merchant_id") or str(self.merchant_id)
		order_id = kwargs.get("order_id") or str(self.order_id)
		currency = kwargs.get("currency", "INR")
		amount = str(kwargs.get("amount", ""))
		redirect_url = kwargs.get("redirect_url") or self.redirect_url
		cancel_url = kwargs.get("cancel_url") or self.cancel_url
		language = kwargs.get("language", "")
		billing_name = kwargs.get("billing_name", "")
		billing_address = kwargs.get("billing_address", "")
		billing_city = kwargs.get("billing_city", "")
		billing_state = kwargs.get("billing_state", "")
		billing_zip = kwargs.get("billing_zip", "")
		billing_country = kwargs.get("billing_country", "")
		billing_tel = kwargs.get("billing_tel", "")
		billing_email = kwargs.get("billing_email", "")
		delivery_name = kwargs.get("delivery_name", "")
		delivery_address = kwargs.get("delivery_address", "")
		delivery_city = kwargs.get("delivery_city", "")
		delivery_state = kwargs.get("delivery_state", "")
		delivery_zip = kwargs.get("delivery_zip", "")
		delivery_country = kwargs.get("delivery_country", "")
		delivery_tel = kwargs.get("delivery_tel", "")
		merchant_param1 = kwargs.get("merchant_param1", "")
		merchant_param2 = kwargs.get("merchant_param2", "")
		merchant_param3 = kwargs.get("merchant_param3", "")
		merchant_param4 = kwargs.get("merchant_param4", "")
		merchant_param5 = kwargs.get("merchant_param5", "")
		integration_type = kwargs.get("integration_type") or "iframe_normal"
		promo_code = kwargs.get("promo_code", "")
		customer_identifier = kwargs.get("customer_identifier", "")

		merchant_data = (
			"merchant_id="
			+ merchant_id
			+ "&"
			+ "order_id="
			+ order_id
			+ "&"
			+ "currency="
			+ currency
			+ "&"
			+ "amount="
			+ amount
			+ "&"
			+ "redirect_url="
			+ redirect_url
			+ "&"
			+ "cancel_url="
			+ cancel_url
			+ "&"
			+ "language="
			+ language
			+ "&"
			+ "billing_name="
			+ billing_name
			+ "&"
			+ "billing_address="
			+ billing_address
			+ "&"
			+ "billing_city="
			+ billing_city
			+ "&"
			+ "billing_state="
			+ billing_state
			+ "&"
			+ "billing_zip="
			+ billing_zip
			+ "&"
			+ "billing_country="
			+ billing_country
			+ "&"
			+ "billing_tel="
			+ billing_tel
			+ "&"
			+ "billing_email="
			+ billing_email
			+ "&"
			+ "delivery_name="
			+ delivery_name
			+ "&"
			+ "delivery_address="
			+ delivery_address
			+ "&"
			+ "delivery_city="
			+ delivery_city
			+ "&"
			+ "delivery_state="
			+ delivery_state
			+ "&"
			+ "delivery_zip="
			+ delivery_zip
			+ "&"
			+ "delivery_country="
			+ delivery_country
			+ "&"
			+ "delivery_tel="
			+ delivery_tel
			+ "&"
			+ "merchant_param1="
			+ merchant_param1
			+ "&"
			+ "merchant_param2="
			+ merchant_param2
			+ "&"
			+ "merchant_param3="
			+ merchant_param3
			+ "&"
			+ "merchant_param4="
			+ merchant_param4
			+ "&"
			+ "merchant_param5="
			+ merchant_param5
			+ "&"
			+ "integration_type="
			+ integration_type
			+ "&"
			+ "promo_code="
			+ promo_code
			+ "&"
			+ "customer_identifier="
			+ customer_identifier
			+ "&"
		)

		return merchant_data

	def validate_mandatory_values(self, **kwargs):
		self.validate_transaction_currency(kwargs.get("currency"))
		if not kwargs.get("amount"):
			frappe.throw(frappe._("Amount is missing"))
		if not kwargs.get("order_id") or hasattr(self, "order_id") and not self.order_id:
			frappe.throw("Param order_id is missing")

	def pad(self, data):
		length = 16 - (len(data) % 16)
		data += chr(length) * length
		return data

	def unpad(self, data):
		padding_length = ord(data[-1])
		return data[:-padding_length]

	def encrypt(self, plain_text, working_key):
		plain_text = self.pad(plain_text).encode("utf-8")

		encDigest = hashlib.md5()
		encDigest.update(working_key.encode("utf-8"))

		enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, self.iv)
		encrypted_text = enc_cipher.encrypt(plain_text)

		return binascii.hexlify(encrypted_text).decode("utf-8")

	def decrypt(self, cipher_text, working_key):
		decDigest = hashlib.md5()
		decDigest.update(working_key.encode("utf-8"))

		encrypted_text = binascii.unhexlify(cipher_text)

		dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, self.iv)
		decrypted_text = dec_cipher.decrypt(encrypted_text).decode("utf-8")

		return self.unpad(decrypted_text)


def get_gateway_controller(doctype, docname, payment_gateway=None):
	if not payment_gateway:
		reference_doc = frappe.get_doc(doctype, docname)
		payment_gateway = reference_doc.payment_gateway
	gateway_controller = frappe.db.get_value("Payment Gateway", payment_gateway, "gateway_controller")
	return gateway_controller
