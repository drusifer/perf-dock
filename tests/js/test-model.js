import {
    displayName,
    formatFrequency,
    iconNameFor,
    profileView,
    sortedGovernors,
    tooltipFor,
    visibleGovernors,
} from '../../shell-extension/lib/model.js';
import {
    normalizeGovernors,
    normalizeSnapshot,
} from '../../shell-extension/lib/contract.js';

function assertEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected))
        throw new Error(`${message}: ${JSON.stringify(actual)} !== ${JSON.stringify(expected)}`);
}

assertEqual(
    visibleGovernors(
        ['performance', 'powersave'],
        ['powersave', 'schedutil', 'performance']
    ),
    ['powersave', 'performance'],
    'availability filtering preserves configured order'
);
assertEqual(
    visibleGovernors(
        ['conservative', 'powersave', 'schedutil', 'performance'],
        ['powersave', 'schedutil', 'performance'],
        'conservative'
    ),
    ['powersave', 'schedutil', 'performance', 'conservative'],
    'current governor is always visible'
);
assertEqual(
    sortedGovernors(['userspace', 'performance', 'ondemand', 'conservative']),
    ['conservative', 'ondemand', 'performance', 'userspace'],
    'menu governors are sorted by display name'
);
assertEqual(displayName('performance'), 'Performance', 'display name');
assertEqual(displayName('some_governor'), 'Some Governor', 'compound display name');
assertEqual(displayName({}), 'Unknown', 'invalid display name is safe');
assertEqual(
    iconNameFor('powersave'),
    'power-profile-power-saver-symbolic',
    'power saver uses a theme icon'
);
assertEqual(
    iconNameFor('conservative'),
    'appointment-soon-symbolic',
    'conservative uses a distinct theme icon'
);
assertEqual(iconNameFor('ondemand'), 'system-run-symbolic', 'ondemand icon');
assertEqual(iconNameFor('userspace'), 'applications-engineering-symbolic', 'userspace icon');
assertEqual(formatFrequency(710400), '710 MHz', 'MHz formatting');
assertEqual(formatFrequency(3420000), '3.42 GHz', 'GHz formatting');

const snapshot = {
    state: 'PERFORMANCE',
    governor: 'performance',
    policy_min: 710400,
    policy_max: 3420000,
    busy: false,
};
assertEqual(
    tooltipFor('performance', snapshot),
    'Performance — Active · favors the highest CPU frequencies',
    'active tooltip identifies the selected governor and its behavior'
);
assertEqual(
    tooltipFor('powersave', snapshot),
    'Powersave — favors lower CPU frequencies',
    'inactive tooltip describes behavior instead of claiming a range'
);

const variant = value => ({deepUnpack: () => value});
assertEqual(
    normalizeGovernors(variant(['powersave', 'performance'])),
    ['powersave', 'performance'],
    'variant governor list is unpacked'
);
assertEqual(
    normalizeSnapshot(variant({
        state: variant('BALANCED'),
        governor: variant('conservative'),
        policy_min: variant(710000),
        policy_max: variant(3420000),
        busy: variant(false),
        ppd_active: variant(true),
    })),
    {
        state: 'BALANCED',
        governor: 'conservative',
        policy_min: 710000,
        policy_max: 3420000,
        hw_min: 0,
        hw_max: 0,
        busy: false,
        ppd_active: true,
    },
    'nested D-Bus variants are normalized'
);
assertEqual(profileView('performance', snapshot).active, true, 'active state');
assertEqual(
    profileView('performance', {...snapshot, state: 'CUSTOM'}).custom,
    true,
    'custom state remains explicit'
);
assertEqual(
    profileView('performance', {...snapshot, state: 'ERROR'}).enabled,
    false,
    'error disables controls'
);
assertEqual(
    profileView('performance', snapshot, true).enabled,
    false,
    'pending disables controls'
);

print('Perf-Dock extension model tests passed');
