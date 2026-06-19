/** @odoo-module **/

import {Component, onWillStart, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

/**
 * Systray bell that surfaces unfinished farm-onboarding sessions.
 *
 * Hidden when the current user has no pending session (count == 0),
 * so non-farm users see nothing. When pending, a pulsing dot draws
 * the eye; click opens the wizard via the existing
 * `action_open_for_current_user` server action.
 *
 * Deliberately lightweight — one `search_count` RPC on mount, no
 * polling. The bell hides immediately on click (optimistic); if the
 * user backs out of the wizard without finishing, the next page
 * reload will surface it again.
 */
export class FarmOnboardingSystray extends Component {
    static template = "farm_onboarding.SystrayBell";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({pending: 0, loaded: false});

        onWillStart(async () => {
            // The systray is registered globally; users without
            // farm_base.group_farm_user will hit AccessError on the
            // search_count. Swallow it so we don't spam the console —
            // a user who can't access the wizard shouldn't see the bell.
            try {
                this.state.pending = await this.orm.call(
                    "farm.onboarding.session",
                    "count_pending_for_current_user",
                    []
                );
            } catch {
                this.state.pending = 0;
            } finally {
                this.state.loaded = true;
            }
        });
    }

    async openWizard() {
        const action = await this.orm.call(
            "farm.onboarding.session",
            "action_open_for_current_user",
            []
        );
        await this.action.doAction(action);
        this.state.pending = 0;
    }
}

registry
    .category("systray")
    .add(
        "farm_onboarding.SystrayBell",
        {Component: FarmOnboardingSystray},
        {sequence: 100}
    );
