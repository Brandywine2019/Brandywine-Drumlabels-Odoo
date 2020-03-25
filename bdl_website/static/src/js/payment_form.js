odoo.define('bld_website.payment_form', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var _t = core._t;
    var PaymentForm = require('payment.payment_form');

    var PaymentFormBDL = PaymentForm.include({
        payEvent: function (ev) {
            ev.preventDefault();
            var button = ev.target;
            var checked_radio = this.$('input[type="radio"]:checked');
            var is_po = $(checked_radio).data("is-po");

            if (is_po ) {
                var po_number = this.$('input[id="po_num_val"]').val();
                if (po_number === "" || !po_number) {
                    this.displayError(
                        _t('No PO Number Entered'),
                        _t('Please enter a PO Number if selecting this payment method.')
                    );
                    this.enableButton(button);
                }
                else {
                    ajax.jsonRpc('/payment/po_number', 'call', {'po_num': po_number}).then(function(data) {
                        console.log("return successful po num");
                    });
                    this._super.apply(this, arguments);
                }
            }
            else {
                this._super.apply(this, arguments);
            }
        },
    });

    return PaymentForm;
});