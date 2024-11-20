$(document).ready(function() {
	var data = {{ frappe.form_dict | json }}; 
    
    frappe.call({
		method: "payments.templates.pages.ccavenue_checkout.get_payment_url",
		freeze: true,
		headers: {
			"X-Requested-With": "XMLHttpRequest"
		},
		args: {
			data: {
                "order_id": data.order_id
            }
		},
		callback: function(r) {
			console.log(r);
			
			if (r.message) {
				window.location.href = r.message.payment_url
			}
		}
	})
})
