/* Start menu favorites, independent of GNOME/taskbar favorites. */
import Gio from 'gi://Gio';
import Shell from 'gi://Shell';
import {EventEmitter} from 'resource:///org/gnome/shell/misc/signals.js';

export class MenuFavorites extends EventEmitter {
    constructor() {
        super();
        const directory = Gio.File.new_for_uri(import.meta.url).get_parent().get_child('schemas');
        const source = Gio.SettingsSchemaSource.new_from_directory(
            directory.get_path(), Gio.SettingsSchemaSource.get_default(), false);
        const schema = source.lookup('org.gnome.shell.extensions.zorin-menu.favorites', false);
        this._settings = new Gio.Settings({settings_schema: schema});
        // Copy the existing list only on the first use. Empty lists stay empty.
        if (!this._settings.get_boolean('initialized')) {
            this._settings.delay();
            this._settings.set_strv('apps', global.settings.get_strv('favorite-apps'));
            this._settings.set_boolean('initialized', true);
            this._settings.apply();
        }
        this._settings.connect('changed::apps', () => this.emit('changed'));
    }

    getFavorites() {
        const system = Shell.AppSystem.get_default();
        return this._settings.get_strv('apps').map(id => system.lookup_app(id)).filter(app => app !== null);
    }

    isFavorite(id) { return this._settings.get_strv('apps').includes(id); }
    isWritable() { return this._settings.is_writable('apps'); }

    toggleFavorite(id) {
        if (!this.isWritable()) return;
        const apps = this._settings.get_strv('apps');
        this._settings.set_strv('apps', apps.includes(id)
            ? apps.filter(app => app !== id) : [...apps, id]);
        // Gio.Settings remains in delayed mode after first-use migration.
        this._settings.apply();
    }
}

let favorites = null;
export function getMenuFavorites() {
    favorites ??= new MenuFavorites();
    return favorites;
}
