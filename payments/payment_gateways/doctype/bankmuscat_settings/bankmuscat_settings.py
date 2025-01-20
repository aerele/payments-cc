# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
# import hashlib
# import binascii
from string import Template
from Crypto.Cipher import AES
from frappe.model.document import Document
from payments.utils import create_payment_gateway
from frappe.utils import get_url, call_hook_method
from frappe.integrations.utils import create_request_log

class BankMuscatSettings(Document):
	supported_currencies = (
				"INR",
				"USD",
				"SGD",
				"GBP",
				"EUR",
				"OMR"
			)
	
	def on_update(self):
		create_payment_gateway(
			"BankMuscat-" + self.merchant_id,
			settings="BankMuscat Settings",
			controller=self.merchant_id,
		)
		call_hook_method(
			"payment_gateway_enabled", gateway="BankMuscat-" + self.merchant_id
		)
	
	def get_payment_url(self, **kwargs):
		frappe.log_error("data: ", kwargs)
		self.order_id = create_request_log(kwargs, service_name="BankMuscat", name=kwargs.get("order_id", "")).name
		return get_url(f"bankmuscat_checkout?order_id={self.order_id}")
	
	def decrypt(self, cipher_text, working_key):
		cipher_text = bytes.fromhex(cipher_text)
		nonce = cipher_text[:AES.block_size]
		ciphertext = cipher_text[16:-16]
		tag = cipher_text[-16:]
		cipher = AES.new(working_key.encode(), AES.MODE_GCM, nonce=nonce)
		plaintext = cipher.decrypt_and_verify(ciphertext, tag)

		return plaintext
	
	def encrypt(self, plain_text, working_key):
		cipher = AES.new(working_key.encode(), AES.MODE_GCM)
		ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())
		encryptedText = (cipher.nonce + ciphertext + tag).hex()

		return encryptedText

	def get_merchant_data(self, **kwargs):
		self.redirect_url = get_url("api/method/payments.templates.pages.bankmuscat_checkout.verify_payment_status")
		self.cancel_url = get_url("api/method/payments.templates.pages.bankmuscat_checkout.cancel_payment")

		merchant_id = kwargs.get('merchant_id') or str(self.merchant_id)
		order_id = kwargs.get('order_id') or str(self.order_id)
		currency = kwargs.get('currency', "INR")
		amount = str(kwargs.get('amount', ""))
		redirect_url = kwargs.get('redirect_url') or self.redirect_url
		cancel_url = kwargs.get('cancel_url') or self.cancel_url
		language = kwargs.get('language', "")
		billing_name = kwargs.get('billing_name', "")
		billing_address = kwargs.get('billing_address', "")
		billing_city = kwargs.get('billing_city', "")
		billing_state = kwargs.get('billing_state', "")
		billing_zip = kwargs.get('billing_zip', "")
		billing_country = kwargs.get('billing_country', "")
		billing_tel = kwargs.get('billing_tel', "")
		billing_email = kwargs.get('billing_email', "")
		delivery_name = kwargs.get('delivery_name', "")
		delivery_address = kwargs.get('delivery_address', "")
		delivery_city = kwargs.get('delivery_city', "")
		delivery_state = kwargs.get('delivery_state', "")
		delivery_zip = kwargs.get('delivery_zip', "")
		delivery_country = kwargs.get('delivery_country', "")
		delivery_tel = kwargs.get('delivery_tel', "")
		merchant_param1 = kwargs.get('merchant_param1', "")
		merchant_param2 = kwargs.get('merchant_param2', "")
		merchant_param3 = kwargs.get('merchant_param3', "")
		merchant_param4 = kwargs.get('merchant_param4', "")
		merchant_param5 = kwargs.get('merchant_param5', "")
		integration_type = kwargs.get('integration_type') or "iframe_normal"
		promo_code = kwargs.get('promo_code', "")
		customer_identifier = kwargs.get('customer_identifier', "")

		merchant_data= ('merchant_id='+merchant_id+'&'+'order_id='+order_id + '&' + "currency=" + currency + \
		'&' +'amount=' + amount+'&'+'redirect_url='+redirect_url+'&'+'cancel_url='+cancel_url+'&'+'language='+language+\
		'&'+'billing_name='+billing_name+'&'+'billing_address='+billing_address+'&'+'billing_city='+billing_city+\
		'&'+'billing_state='+billing_state+'&'+'billing_zip='+billing_zip+'&'+'billing_country='+billing_country+\
		'&'+'billing_tel='+billing_tel+'&'+'billing_email='+billing_email+'&'+'delivery_name='+delivery_name+\
		'&'+'delivery_address='+delivery_address+'&'+'delivery_city='+delivery_city+'&'+'delivery_state='+delivery_state+\
		'&'+'delivery_zip='+delivery_zip+'&'+'delivery_country='+delivery_country+'&'+'delivery_tel='+delivery_tel+\
		'&'+'merchant_param1='+merchant_param1+'&'+'merchant_param2='+merchant_param2+'&'+'merchant_param3='+merchant_param3+\
		'&'+'merchant_param4='+merchant_param4+'&'+'merchant_param5='+merchant_param5+\
		'&'+'integration_type='+integration_type+'&'+'promo_code='+promo_code+\
		'&'+'customer_identifier='+customer_identifier+'&')

		return merchant_data

	def get_encrypted_request(self, **kwargs):
		merchant_data = self.get_merchant_data(**kwargs)
		
		return self.encrypt(merchant_data, self.get_password('working_key'))

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(
				frappe._(
					"Please select another payment method. BankMuscat does not support transactions in currency '{0}'"
				).format(currency)
			)
	
	def validate_mandatory_values(self, **kwargs):
		self.validate_transaction_currency(kwargs.get('currency'))
		if not kwargs.get('amount'):
			frappe.throw(frappe._("Amount is missing"))
		if not kwargs.get('order_id') or hasattr(self, 'order_id') and not self.order_id:
			frappe.throw("Param order_id is missing")

	def get_gateway_url(self, template= False, **kwargs):
		self.validate_mandatory_values(**kwargs)
		encrypted_req = self.get_encrypted_request(**kwargs)

		iframe = """
		<iframe  
			width="482" height="500" scrolling="No" frameborder="0"  id="paymentFrame"
			src="https://www.hospitalshop.com/transaction.do?command=initiateTransaction&encReq=$encReq&xscode=$xscode">
	  	</iframe>
		"""

		formated_template = Template(iframe).safe_substitute(
			encReq=encrypted_req,
			xscode=self.get_password('access_code')
		)
		if template:
			return formated_template

		from bs4 import BeautifulSoup
		return BeautifulSoup(formated_template, 'html.parser').find('iframe')['src']
	
	def get_payment_page_url(self, **kwargs):
		return self.get_gateway_url(template=False, **kwargs)
	
def get_gateway_controller(doctype, docname, payment_gateway=None):
	if not payment_gateway:
		reference_doc = frappe.get_doc(doctype, docname)
		payment_gateway = reference_doc.payment_gateway
	gateway_controller = frappe.db.get_value("Payment Gateway", payment_gateway, "gateway_controller")
	return gateway_controller