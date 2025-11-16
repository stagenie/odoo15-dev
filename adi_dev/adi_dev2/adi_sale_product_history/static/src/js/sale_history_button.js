odoo.define('adi_sale_product_history.SaleHistoryButton', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');
    var core = require('web.core');
    var _t = core._t;

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .o_history_button': '_onClickHistory',
        }),

        _onClickHistory: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            
            var $row = $(ev.currentTarget).closest('tr');
            var productId = $row.find('td[name="product_id"] input').val();
            
            if (!productId) {
                return this.do_warn(_t('Attention'), _t('Veuillez d\'abord sélectionner un produit.'));
            }

            this._rpc({
                model: 'sale.order.line',
                method: 'action_view_product_history',
                args: [false],
                kwargs: {
                    context: {
                        'default_product_id': parseInt(productId),
                    },
                },
            }).then(function (action) {
                this.do_action(action);
            }.bind(this));
        },
    });
}