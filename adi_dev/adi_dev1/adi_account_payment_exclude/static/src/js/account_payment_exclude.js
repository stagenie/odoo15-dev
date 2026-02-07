odoo.define('adi_account_payment_exclude.payment', function (require) {
"use strict";

var ShowPaymentLineWidget = require('account.payment').ShowPaymentLineWidget;

ShowPaymentLineWidget.include({
    events: _.extend({
        'click .outstanding_credit_exclude': '_onOutstandingCreditExclude',
    }, ShowPaymentLineWidget.prototype.events),

    /**
     * Handler pour exclure une ligne du rapprochement facture.
     * Appelle le backend pour marquer la ligne comme exclue puis recharge.
     */
    _onOutstandingCreditExclude: function (event) {
        event.stopPropagation();
        event.preventDefault();
        var self = this;
        var $target = $(event.target).closest('.outstanding_credit_exclude');
        var id = $target.data('id') || false;
        if (!id) {
            return;
        }
        this._rpc({
            model: 'account.move.line',
            method: 'action_exclude_from_invoice_tab',
            args: [[id]],
        }).then(function () {
            self.trigger_up('reload');
        });
    },
});

});
