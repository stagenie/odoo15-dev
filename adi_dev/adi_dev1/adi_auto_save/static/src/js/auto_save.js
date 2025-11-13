/** @odoo-module **/

import { FormController } from '@web/views/form/form_controller';
import { patch } from 'web.utils';
import { useService } from "@web/core/utils/hooks";

const { onWillStart, onMounted, onWillUnmount } = owl;

patch(FormController.prototype, 'adi_auto_save.FormController', {
    setup() {
        this._super(...arguments);
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.autoSaveTimer = null;
        this.autoSaveEnabled = false;
        this.autoSaveInterval = 30000; // 30 secondes par défaut

        onWillStart(async () => {
            await this._loadAutoSaveConfig();
        });

        onMounted(() => {
            this._setupAutoSave();
        });

        onWillUnmount(() => {
            this._clearAutoSave();
        });
    },

    /**
     * Charge la configuration de l'auto-save depuis les paramètres
     */
    async _loadAutoSaveConfig() {
        try {
            const result = await this.rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['adi_auto_save.auto_save_enabled', 'True'],
            });
            this.autoSaveEnabled = result === 'True';

            if (this.autoSaveEnabled) {
                const interval = await this.rpc({
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['adi_auto_save.auto_save_interval', '30'],
                });
                this.autoSaveInterval = parseInt(interval) * 1000;
            }
        } catch (error) {
            console.error('Erreur lors du chargement de la configuration auto-save:', error);
        }
    },

    /**
     * Configure l'auto-save pour les modèles supportés
     */
    _setupAutoSave() {
        if (!this.autoSaveEnabled) {
            return;
        }

        const modelName = this.props.resModel;
        const supportedModels = ['sale.order', 'purchase.order'];

        if (!supportedModels.includes(modelName)) {
            return;
        }

        // Vérifier si ce modèle spécifique est activé
        this._checkModelEnabled(modelName).then(enabled => {
            if (enabled) {
                this._startAutoSave();
            }
        });
    },

    /**
     * Vérifie si l'auto-save est activé pour un modèle spécifique
     */
    async _checkModelEnabled(modelName) {
        try {
            let paramName = '';
            if (modelName === 'sale.order') {
                paramName = 'adi_auto_save.auto_save_sale_order';
            } else if (modelName === 'purchase.order') {
                paramName = 'adi_auto_save.auto_save_purchase_order';
            }

            if (paramName) {
                const result = await this.rpc({
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: [paramName, 'True'],
                });
                return result === 'True';
            }
        } catch (error) {
            console.error('Erreur lors de la vérification du modèle:', error);
        }
        return false;
    },

    /**
     * Démarre le timer d'auto-save
     */
    _startAutoSave() {
        this._clearAutoSave();
        this.autoSaveTimer = setInterval(() => {
            this._performAutoSave();
        }, this.autoSaveInterval);
    },

    /**
     * Arrête le timer d'auto-save
     */
    _clearAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    },

    /**
     * Effectue la sauvegarde automatique
     */
    async _performAutoSave() {
        // Ne pas sauvegarder si :
        // - Le formulaire n'est pas en mode édition
        // - Il n'y a pas de changements
        // - Le record n'existe pas encore (nouveau record non sauvegardé)
        if (!this.model.root.isInEdition ||
            !this.model.root.isDirty ||
            !this.model.root.resId) {
            return;
        }

        try {
            // Sauvegarder le formulaire
            await this.model.root.save();

            // Afficher une notification discrète
            this.notification.add(
                'Enregistrement automatique effectué',
                {
                    type: 'info',
                    sticky: false,
                    className: 'o_auto_save_notification',
                }
            );
        } catch (error) {
            console.error('Erreur lors de l\'enregistrement automatique:', error);
            // Ne pas afficher d'erreur à l'utilisateur pour ne pas le distraire
            // sauf si c'est une erreur critique
            if (error.message && !error.message.includes('save')) {
                this.notification.add(
                    'Erreur lors de l\'enregistrement automatique',
                    {
                        type: 'warning',
                        sticky: false,
                    }
                );
            }
        }
    },

    /**
     * Surcharge de la méthode saveRecord pour réinitialiser le timer
     */
    async saveButtonClicked(params = {}) {
        await this._super(...arguments);
        // Réinitialiser le timer après une sauvegarde manuelle
        if (this.autoSaveEnabled) {
            this._startAutoSave();
        }
    },
});
