import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

import {createControlProxy} from './lib/dbus.js';
import {normalizeGovernors, normalizeSnapshot} from './lib/contract.js';
import {
    displayName,
    iconNameFor,
    profileView,
    sortedGovernors,
} from './lib/model.js';

const ProfileButton = GObject.registerClass(
class ProfileButton extends St.Button {
    _init(extension, governor, activate) {
        super._init({
            style_class: 'perf-dock-button',
            reactive: true,
            can_focus: true,
            track_hover: true,
            toggle_mode: true,
        });
        this._extension = extension;
        this.governor = governor;
        this._icon = new St.Icon({
            icon_name: iconNameFor(governor),
            style_class: 'system-status-icon',
        });
        this.set_child(this._icon);
        this.connect('button-press-event', () => {
            activate(governor);
            return Clutter.EVENT_STOP;
        });
        this.connect('enter-event', () => {
            this._extension.showTooltip(this);
            return Clutter.EVENT_PROPAGATE;
        });
        this.connect('leave-event', () => {
            this._extension.hideTooltip();
            return Clutter.EVENT_PROPAGATE;
        });
        this.connect('key-focus-in', () => this._extension.showTooltip(this));
        this.connect('key-focus-out', () => this._extension.hideTooltip());
    }

    update(view) {
        this.view = view;
        this.accessible_name = view.tooltip;
        this.checked = view.active;
        this.set_style_class_name('perf-dock-button');
        if (view.active)
            this.add_style_class_name('perf-dock-button-active');
        if (view.pending)
            this.add_style_class_name('perf-dock-button-pending');
        if (!view.enabled && !view.pending)
            this.add_style_class_name('perf-dock-button-error');
        this.reactive = view.enabled;
    }
});

const MenuButton = GObject.registerClass(
class MenuButton extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'Perf-Dock Profiles', true);
        this.profileBox = new St.BoxLayout({style_class: 'perf-dock-profile-box'});
        this.add_child(this.profileBox);
    }
});

export default class PerfDockExtension extends Extension {
    enable() {
        this._buttons = new Map();
        this._snapshot = {state: 'ERROR', governor: '', busy: false};
        this._available = [];
        this._pending = false;
        this._restarting = false;
        this._tooltip = new St.Label({style_class: 'perf-dock-tooltip'});
        Main.layoutManager.addChrome(this._tooltip);
        this._tooltip.hide();
        this._menuButton = new MenuButton();
        Main.panel.addToStatusArea(`${this.uuid}-menu`, this._menuButton);
        this._connectBackend();
    }

    async _connectBackend() {
        try {
            this._proxy = await createControlProxy(this);
            this._ownerChanged = this._proxy.connect('notify::g-name-owner', () => {
                if (this._proxy.g_name_owner)
                    this._refresh();
                else if (!this._restarting)
                    this._recoverBackend();
            });
            this._snapshotSignal = this._proxy.connectSignal(
                'SnapshotChanged', (_proxy, _sender, [snapshot]) => {
                    this._snapshot = normalizeSnapshot(snapshot);
                    this._pending = false;
                    this._rebuildProfileButtons();
                }
            );
            await this._refresh();
        } catch (error) {
            console.warn(`Perf-Dock backend unavailable: ${error.message}`);
            this._setUnavailable();
        }
    }

    async _refresh() {
        const [governors] = await this._proxy.GetGovernorsAsync();
        const [snapshot] = await this._proxy.GetSnapshotAsync();
        this._available = normalizeGovernors(governors);
        this._snapshot = normalizeSnapshot(snapshot);
        this._pending = false;
        this._rebuildProfileButtons();
    }

    _rebuildProfileButtons() {
        if (!this._buttons)
            return;
        for (const button of this._buttons.values())
            button.destroy();
        this._buttons.clear();
        const names = sortedGovernors(this._available);
        names.forEach(governor => {
            const button = new ProfileButton(
                this, governor, name => this._setGovernor(name)
            );
            this._buttons.set(governor, button);
            this._menuButton.profileBox.add_child(button);
        });
        this._updateViews();
    }

    async _setGovernor(governor) {
        if (this._pending)
            return;
        this._pending = true;
        this._updateViews();
        try {
            const [accepted, message] = await this._proxy.SetGovernorAsync(governor);
            if (!accepted)
                Main.notifyError('Perf-Dock', message);
            await this._refresh();
        } catch (error) {
            console.error(`Perf-Dock could not change governor: ${error.message}`);
            Main.notifyError('Perf-Dock', `Could not change governor: ${error.message}`);
            this._setUnavailable();
        }
    }

    _updateViews() {
        for (const [governor, button] of this._buttons)
            button.update(profileView(governor, this._snapshot, this._pending));
        if (this._menuButton) {
            this._menuButton.accessible_name = this._statusText();
        }
    }

    _statusText() {
        if (this._restarting)
            return 'Perf-Dock: Restarting backend…';
        if (this._snapshot.state === 'ERROR')
            return 'Perf-Dock: Backend problem — retrying…';
        const custom = this._snapshot.state === 'CUSTOM' ? 'Custom — ' : '';
        return `Perf-Dock: ${custom}${displayName(this._snapshot.governor)}`;
    }

    async _recoverBackend() {
        if (this._restarting)
            return;
        this._restarting = true;
        this._updateViews();
        for (let attempt = 0; attempt < 5; attempt++) {
            await new Promise(resolve => {
                GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => {
                    resolve();
                    return GLib.SOURCE_REMOVE;
                });
            });
            try {
                await this._refresh();
                this._restarting = false;
                this._updateViews();
                return;
            } catch (error) {
                console.debug(`Perf-Dock reconnect attempt failed: ${error.message}`);
            }
        }
        this._restarting = false;
        this._setUnavailable();
    }

    _setUnavailable() {
        this._snapshot = {state: 'ERROR', governor: '', busy: false};
        this._pending = false;
        this._updateViews();
    }

    showTooltip(button) {
        if (!button.view)
            return;
        this._tooltip.text = button.view.tooltip;
        const [x, y] = button.get_transformed_position();
        this._tooltip.set_position(x, y + button.height + 6);
        this._tooltip.show();
    }

    hideTooltip() {
        this._tooltip?.hide();
    }

    disable() {
        this.hideTooltip();
        this._tooltip?.destroy();
        this._tooltip = null;
        if (this._proxy && this._ownerChanged)
            this._proxy.disconnect(this._ownerChanged);
        if (this._proxy && this._snapshotSignal)
            this._proxy.disconnectSignal(this._snapshotSignal);
        for (const button of this._buttons?.values() ?? [])
            button.destroy();
        this._buttons = null;
        this._menuButton?.destroy();
        this._menuButton = null;
        this._proxy = null;
    }
}
