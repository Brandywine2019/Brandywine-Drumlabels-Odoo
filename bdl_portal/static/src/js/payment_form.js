odoo.define('bld_portal.payment_form', function (require) {
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

    var PaymentFormShipBDL = PaymentForm.include({
        payEvent: function (ev) {
            ev.preventDefault();

            var ship_instructions = this.$('textarea[name="shipping_instructions"]').val();
            console.log(ship_instructions)
            if (ship_instructions) {
                ajax.jsonRpc('/payment/ship_instructions', 'call', {'ship_instructions': ship_instructions}).then(function(data) {
                    console.log("return successful shipping instructions");
                });
            }
            this._super.apply(this, arguments);
        },
    });

    return PaymentForm;
});