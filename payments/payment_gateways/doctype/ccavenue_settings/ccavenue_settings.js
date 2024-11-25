// Copyright (c) 2024, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("CCAvenue Settings", {
    refresh(frm) {
    if(!frm.is_new()){
        frm.add_custom_button(__('Make Payment'), () => {
            makePaymentDialog(frm)
        })
    }
    },
});

let makePaymentDialog = (frm) => {
//new dialog for payment checkout
    let dialog = new frappe.ui.Dialog({
            title: 'Payment Details',
            size: "large",
            fields: [
                    {
                            label: 'Merchant Id',
                            fieldname: 'merchant_id',
                            fieldtype: 'Data',
                            default: frm.doc.merchant_id,
                            read_only: 1,
                    },
                    {
                            fieldtype: 'Column Break',
                    },
                    {
                            label: 'Order Id',
                            fieldname: 'order_id',
                            fieldtype: 'Data',
                            reqd: 1 
                    },
                    {
                            fieldtype: 'Section Break',
                    },
                    {
                            label: 'Currency',
                            fieldname: 'currency',
                            fieldtype: 'Select',
                            options: ["INR", "USD", "SGD", "GBP", "EUR"],
                            reqd: 1 
                    },
                    {
                            label: 'Amount',
                            fieldname: 'amount',
                            fieldtype: 'Currency',
                            options: "currency",
                            reqd: 1 
                    },
                    {
                            fieldtype: 'Section Break',
                    },
                    {
                            fieldname: 'iframe_section1',
                            fieldtype: 'HTML'
                    }
            ],
            primary_action_label: 'Checkout',
            primary_action: function() {
                    frappe.call({
                            method: "get_iframe_template",
                            doc: frm.doc,
                            args: {
                                    merchant_id : dialog.get_value('merchant_id'),
                                    order_id : dialog.get_value('order_id'),
                                    currency : dialog.get_value('currency'),
                                    amount : dialog.get_value('amount'),
                                    redirect_url : dialog.get_value('redirect_url'),
                                    cancel_url : dialog.get_value('cancel_url'),
                                    language : dialog.get_value('language'),
                                    billing_name : dialog.get_value('billing_name'),
                                    billing_address : dialog.get_value('billing_address'),
                                    billing_city : dialog.get_value('billing_city'),
                                    billing_state : dialog.get_value('billing_state'),
                                    billing_zip : dialog.get_value('billing_zip'),
                                    billing_country : dialog.get_value('billing_country'),
                                    billing_tel : dialog.get_value('billing_tel'),
                                    billing_email : dialog.get_value('billing_email'),
                                    delivery_name : dialog.get_value('delivery_name'),
                                    delivery_address : dialog.get_value('delivery_address'),
                                    delivery_city : dialog.get_value('delivery_city'),
                                    delivery_state : dialog.get_value('delivery_state'),
                                    delivery_zip : dialog.get_value('delivery_zip'),
                                    delivery_country : dialog.get_value('delivery_country'),
                                    delivery_tel : dialog.get_value('delivery_tel'),
                                    merchant_param1 : dialog.get_value('merchant_param1'),
                                    merchant_param2 : dialog.get_value('merchant_param2'),
                                    merchant_param3 : dialog.get_value('merchant_param3'),
                                    merchant_param4 : dialog.get_value('merchant_param4'),
                                    merchant_param5 : dialog.get_value('merchant_param5'),
                                    integration_type : dialog.get_value('integration_type'),
                                    promo_code : dialog.get_value('promo_code'),
                                    customer_identifier : dialog.get_value('customer_identifier'),
                            },
                            callback: function (res) {
                                    if (res.message) {
                                        window.open(res.message, '_blank', 'width=800,height=600')
                                    }
                            },
                    });
            }
    });

    dialog.show()
}
