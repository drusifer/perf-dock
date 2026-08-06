import Gio from 'gi://Gio';

export const BUS_NAME = 'io.github.perf_dock';
export const OBJECT_PATH = '/io/github/perf_dock';

function loadInterfaceXml(extension) {
    const file = extension.dir
        .get_child('dbus')
        .get_child('io.github.perf_dock.Control1.xml');
    const [ok, contents] = file.load_contents(null);
    if (!ok)
        throw new Error('Could not load the Perf-Dock D-Bus contract');
    return new TextDecoder().decode(contents);
}

export async function createControlProxy(extension, cancellable = null) {
    const Proxy = Gio.DBusProxy.makeProxyWrapper(loadInterfaceXml(extension));
    return await new Promise((resolve, reject) => {
        Proxy(
            Gio.DBus.session,
            BUS_NAME,
            OBJECT_PATH,
            (proxy, error) => error ? reject(error) : resolve(proxy),
            cancellable,
            Gio.DBusProxyFlags.NONE
        );
    });
}
