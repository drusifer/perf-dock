export const DEFAULT_VISIBLE = ['powersave', 'schedutil', 'performance'];

export function visibleGovernors(available, configured, current = '') {
    const availableSet = new Set(available);
    const visible = configured.filter(name => availableSet.has(name));
    if (availableSet.has(current) && !visible.includes(current))
        visible.push(current);
    return visible;
}

export function sortedGovernors(governors) {
    return [...governors].sort((left, right) =>
        displayName(left).localeCompare(displayName(right))
    );
}

export function displayName(governor) {
    if (typeof governor !== 'string' || !governor)
        return 'Unknown';

    return governor
        .split(/[-_]/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

const GOVERNOR_ICONS = {
    powersave: 'power-profile-power-saver-symbolic',
    schedutil: 'power-profile-balanced-symbolic',
    performance: 'power-profile-performance-symbolic',
    conservative: 'appointment-soon-symbolic',
    ondemand: 'system-run-symbolic',
    userspace: 'applications-engineering-symbolic',
};

const GOVERNOR_DESCRIPTIONS = {
    powersave: 'favors lower CPU frequencies',
    schedutil: 'scheduler-guided frequency scaling',
    performance: 'favors the highest CPU frequencies',
    conservative: 'raises frequency gradually under load',
    ondemand: 'raises frequency quickly under load',
    userspace: 'frequency controlled by userspace',
};

export function iconNameFor(governor) {
    return GOVERNOR_ICONS[governor] ?? 'applications-system-symbolic';
}

export function formatFrequency(khz) {
    if (!khz)
        return 'unknown';
    if (khz >= 1_000_000)
        return `${(khz / 1_000_000).toFixed(2).replace(/\.00$/, '')} GHz`;
    return `${Math.round(khz / 1000)} MHz`;
}

export function tooltipFor(governor, snapshot) {
    const description = GOVERNOR_DESCRIPTIONS[governor] ??
        'CPU frequency scaling governor';
    const active = snapshot.governor === governor ? 'Active · ' : '';
    return `${displayName(governor)} — ${active}${description}`;
}

export function profileView(governor, snapshot, pending = false) {
    const unavailable = snapshot.state === 'ERROR';
    return {
        governor,
        label: displayName(governor),
        active: !unavailable && snapshot.governor === governor,
        custom: snapshot.state === 'CUSTOM' && snapshot.governor === governor,
        pending,
        enabled: !unavailable && !pending && !snapshot.busy,
        tooltip: tooltipFor(governor, snapshot),
    };
}
