odoo.define('hide_rainbow_man.HideRainbowMan', function (require) {
    "use strict";

    const session = require('web.session');
    const AbstractAction = require('web.AbstractAction');
    const originalShowEffect = AbstractAction.prototype.show_effect;

    AbstractAction.include({
        show_effect: function (options) {
            // Désactiver le Rainbow Man uniquement pour la réconciliation
            if (options && options.message && options.message.includes('Réconcilié')) {
                return; // Ignore l'effet
            }
            // Appeler le comportement d'origine pour les autres cas
            return originalShowEffect.apply(this, arguments);
        },
    });
});
