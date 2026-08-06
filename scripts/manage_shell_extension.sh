#!/usr/bin/env bash
set -euo pipefail

readonly action="${1:-check}"
readonly uuid="perf-dock@drusifer"
readonly data_root="${XDG_DATA_HOME:-${HOME}/.local/share}"
readonly extension_dir="${data_root}/gnome-shell/extensions/${uuid}"
readonly service_dir="${data_root}/dbus-1/services"
readonly service_file="${service_dir}/io.github.perf_dock.service"

shell_major() {
    gnome-shell --version | awk '{split($3, version, "."); print version[1]}'
}

validate() {
    command -v gnome-shell >/dev/null
    command -v gnome-extensions >/dev/null
    command -v glib-compile-schemas >/dev/null
    if [[ "$(shell_major)" != "50" ]]; then
        echo "Perf-Dock supports GNOME Shell 50; found $(gnome-shell --version)." >&2
        exit 2
    fi
}

is_registered() {
    local installed_uuid
    while IFS= read -r installed_uuid; do
        [[ "$installed_uuid" == "$uuid" ]] && return 0
    done < <(gnome-extensions list --user)
    return 1
}

install_extension() {
    validate
    local executable
    executable="$(command -v perf-dock || true)"
    if [[ -z "$executable" || ! -x "$executable" ]]; then
        echo "perf-dock is not installed on PATH; run 'make install' first." >&2
        exit 2
    fi
    local bundle temporary_dir
    temporary_dir="$(mktemp -d)"
    bundle="${temporary_dir}/${uuid}.shell-extension.zip"
    trap 'rm -rf -- "$temporary_dir"' RETURN
    gnome-extensions pack --force --out-dir "$temporary_dir" \
        --extra-source=lib \
        --extra-source=dbus \
        --extra-source=icons \
        --schema=schemas/org.gnome.shell.extensions.perf-dock.gschema.xml \
        shell-extension
    gnome-extensions install --force "$bundle"
    install -d -m 0755 "$service_dir"
    sed "s|@PERF_DOCK_EXEC@|$executable|g" \
        packaging/io.github.perf_dock.service.in >"$service_file"
    chmod 0644 "$service_file"
    rm -rf -- "$temporary_dir"
    trap - RETURN
    echo "Installed $uuid for $(gnome-shell --version)."
}

case "$action" in
    check)
        validate
        echo "GNOME Shell extension prerequisites passed."
        ;;
    install)
        install_extension
        ;;
    enable)
        validate
        if ! is_registered; then
            echo "$uuid is installed but not loaded by the running Shell." >&2
            echo "On Wayland, log out and back in, then rerun make enable-extension." >&2
            exit 3
        fi
        gnome-extensions enable "$uuid"
        echo "Enabled $uuid."
        ;;
    reload)
        validate
        if is_registered; then
            gnome-extensions disable "$uuid" 2>/dev/null || true
            gnome-extensions enable "$uuid"
            echo "Restarted $uuid's extension lifecycle."
            echo "GNOME Shell may retain imported JavaScript until the next login."
        elif gdbus call --session \
            --dest org.gnome.Shell.Extensions \
            --object-path /org/gnome/Shell/Extensions \
            --method org.gnome.Shell.Extensions.ReloadExtension "$uuid"; then
            gnome-extensions enable "$uuid"
            echo "Discovered and enabled $uuid in the running Shell."
        else
            echo "GNOME Shell could not discover a newly installed extension." >&2
            echo "Log out and back in once, then run make enable-extension." >&2
            exit 3
        fi
        ;;
    disable)
        gnome-extensions disable "$uuid"
        echo "Disabled $uuid."
        ;;
    uninstall)
        gnome-extensions disable "$uuid" 2>/dev/null || true
        if [[ "$extension_dir" == */gnome-shell/extensions/"$uuid" ]]; then
            rm -rf -- "$extension_dir"
        else
            echo "Refusing unexpected extension path: $extension_dir" >&2
            exit 2
        fi
        rm -f -- "$service_file"
        echo "Uninstalled $uuid; the system Polkit helper was preserved."
        ;;
    *)
        echo "Usage: $0 check|install|enable|reload|disable|uninstall" >&2
        exit 2
        ;;
esac
