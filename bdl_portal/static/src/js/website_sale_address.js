odoo.define('bdl_portal.website_sale_cart', function(require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.websiteSaleCartBDL = sAnimations.Class.extend({
	selector: '.oe_website_sale .oe_cart',
	read_events: {
	    'click .js_change_billing': '_onClickChangeBilling',
	    'click .js_add_billing': '_onClickAddBillingAddress',
	},

	//--------------------------------------------------------------------------
	// Handlers
	//--------------------------------------------------------------------------

	/**
	 * @private
	 * @param {Event} ev
	 */
	_onClickChangeBilling: function (ev) {
	    var $old = $('.all_billing').find('.card.border_primary');
	    $old.find('.btn-bill').toggle();
	    $old.addClass('js_change_billing');
	    $old.removeClass('border_primary');

	    var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
	    $new.find('.btn-bill').toggle();
	    $new.removeClass('js_change_billing');
	    $new.addClass('border_primary');

	    var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
	    $.post($form.attr('action'), $form.serialize()+'&xhr=1');
	},

	_onClickAddBillingAddress: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address_add_billing').submit();
    },
});
});
