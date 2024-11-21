// Copyright (c) 2024, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Gateway Settings", {
    refresh(frm){
        frm.trigger("update_query_filters")
    },

    update_query_filters(frm){
        frm.set_query("gateway_settings", "default_gateways", (frm, cdt, cdn)=>{
            return {
                filters: {
                    "module": "Payment Gateways",
                    "name": ["not in", cur_frm.doc.default_gateways.map((acc)=>{return acc.gateway_settings})]
                }
            }
        })

        frm.set_query("payment_gateway", "default_gateways", (frm, cdt, cdn)=>{
            let row = locals[cdt][cdn]
            return {
                filters: {
                    "gateway_settings": row.gateway_settings
                }
            }
        })

        frm.set_query("payment_gateway_account", "default_gateways", (frm, cdt, cdn)=>{
            let row = locals[cdt][cdn]
            return {
                filters: {
                    "payment_gateway": row.payment_gateway,
                    "company": row.company
                }
            }
        })
    },

    validate(frm){
        if(frm.doc.gateway_mode == "Default"){
            cur_frm.clear_table("default_gateways")
        }
    },
});

frappe.ui.form.on("Default Gateway", {
	payment_gateway(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        frappe.db.get_value(
            "DocType",
            { name: row.payment_gateway},
            "issingle",
            (r) => {
                if(r.issingle){
                    frappe.model.set_value(cdt, cdn, "single", r.issingle)
                }
                else{
                    this.update_payemnt_gateway(frm, row.payment_gateway, cdt, cdn)
                }
            }
        );
    },

    default_gateway(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        if(row.default_gateway == "No Records"){
            frappe.model.set_value(cdt, cdn, "default_gateway", "")
        }
    }
});

this.update_payemnt_gateway = function(frm, payment_gateway, cdt, cdn){
    frm.call({
        doc: frm.doc,
        method: "get_gateway_list",
        args: {
            doctype: payment_gateway
        },
        callback: function (r) {
            if(r.message.options && !r.exc){
                frm.fields_dict.default_gateways.grid.update_docfield_property('default_gateway', 'options', r.message.options);
            }
        },
      });
}