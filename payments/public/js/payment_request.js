frappe.ui.form.on('Payment Request', {
	refresh(frm) {        
        frm.toggle_display("default_gateway_accounts", frm.doc.default_gateway_accounts.length)

		frm.set_query("payment_gateway_account", function(){
			return {
				filters: {
					"company": frm.doc.company
				}
			}
		})
	}
})