/** @odoo-module **/

import { session } from '@web/session';
import { registry } from '@web/core/registry';

const { Component, xml } = owl;

class DemoBanner extends Component {

    setup() {
        this.bannerText = session.demo_banner_text || '\u26a0 BASE DEMO - Formation \u26a0';
        this.isVisible = session.demo_banner_enabled;
    }
}

DemoBanner.template = 'adi_demo_banner.DemoBanner';

if (session.demo_banner_enabled) {
    registry.category('main_components').add('DemoBanner', {
        Component: DemoBanner,
    });
}
