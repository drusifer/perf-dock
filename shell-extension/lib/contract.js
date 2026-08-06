function unpack(value) {
    let current = value;
    const seen = new Set();

    while (current !== null && typeof current === 'object') {
        if (seen.has(current))
            break;
        seen.add(current);

        if (typeof current.deepUnpack === 'function')
            current = current.deepUnpack();
        else if (typeof current.unpack === 'function')
            current = current.unpack();
        else
            break;
    }

    if (Array.isArray(current))
        return current.map(item => unpack(item));
    if (current !== null && typeof current === 'object') {
        return Object.fromEntries(
            Object.entries(current).map(([key, item]) => [key, unpack(item)])
        );
    }
    return current;
}

export function normalizeGovernors(raw) {
    const governors = unpack(raw);
    if (!Array.isArray(governors))
        return [];
    return governors.map(governor => String(governor));
}

export function normalizeSnapshot(raw) {
    const snapshot = unpack(raw) ?? {};
    return {
        state: String(snapshot.state ?? 'ERROR'),
        governor: String(snapshot.governor ?? ''),
        policy_min: Number(snapshot.policy_min ?? 0),
        policy_max: Number(snapshot.policy_max ?? 0),
        hw_min: Number(snapshot.hw_min ?? 0),
        hw_max: Number(snapshot.hw_max ?? 0),
        busy: Boolean(snapshot.busy ?? false),
        ppd_active: Boolean(snapshot.ppd_active ?? false),
    };
}
