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
		if(frm.doc.status != "Paid" && frm.doc.transaction_status){
			frm.dashboard.add_comment(frm.doc.transaction_status, "red", true)
		}
		else if(frm.doc.status == "Paid"){
			frm.dashboard.add_comment(frm.doc.transaction_status, "green", true)
		}
	}
})