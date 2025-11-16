odoo.define('adi_hide_rainbow.disable_rainbow_man', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');

    var _t = core._t;

    // Surcharge de la fonction d'affichage du Rainbow Man
    function overrideRainbowMan() {
        var originalShowEffect = core.action_registry.get('effect');
        if (originalShowEffect) {
            core.action_registry.add('effect', function (parent, action) {
                if (action.effect === 'rainbow_man') {
                    // Vérifier si le Rainbow Man est désactivé dans les paramètres
                    session.user_has_group('base.group_system').then(function (is_admin) {
                        if (is_admin) {
                            parent.trigger_up('show_effect', action);
                        } else {
                            console.log("Rainbow Man désactivé");
                        }
                    });
                } else {
                    return originalShowEffect(parent, action);
                }
            });
        }
    }

    // Appeler la fonction de surcharge au chargement du module
    overrideRainbowMan();
});