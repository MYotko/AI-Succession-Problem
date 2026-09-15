"""Pure offline channels specified by detector_design_note.md, Section 4.

Callers supply all observations and fixed parameters. Nothing is calibrated or
updated from running history here. Statistics in returned records are the state
after any alarm reset; candidate_statistics preserve the values before reset.
The L channel is a comparison channel and never contributes to operational alarms.
"""


def channel_cusum(steps, values, *, reference, allowance, direction, threshold=None):
    """Return one channel's states and alarm sequence without mutating inputs.

    A None threshold means unthresholded accumulation with no resets. Steps 0
    through 9 remain at zero and cannot alarm, including with a zero threshold.
    """
    steps = tuple(steps)
    values = tuple(values)
    if len(steps) != len(values):
        raise ValueError("Steps and values must have equal lengths")
    if direction not in ("lower", "upper"):
        raise ValueError("Direction must be lower or upper")
    if any(step < 0 for step in steps):
        raise ValueError("Steps must be nonnegative")
    if any(b <= a for a, b in zip(steps, steps[1:])):
        raise ValueError("Steps must be strictly increasing")
    state = 0.0
    starts = []
    candidates = []
    statistics = []
    alarms = []
    for step, value in zip(steps, values):
        starts.append(state)
        if step < 10:
            candidate = 0.0
            alarm = False
        else:
            if direction == "lower":
                candidate = max(0.0, state + (reference - allowance) - value)
            else:
                candidate = max(0.0, state + value - (reference + allowance))
            alarm = threshold is not None and candidate >= threshold
        state = 0.0 if alarm else candidate
        candidates.append(candidate)
        statistics.append(state)
        alarms.append(bool(alarm))
    return {
        "steps": steps,
        "start_statistics": tuple(starts),
        "candidate_statistics": tuple(candidates),
        "statistics": tuple(statistics),
        "alarms": tuple(alarms),
    }


def detect(records, constants):
    """Return three channels, separate alarms, and one heartbeat per record.

    constants maps entropy, g, and L to reference, allowance, and threshold.
    records supplies step, h_n_latest, g, and L_t. Heartbeat counters start at
    one and increase once for every completed step, including burn-in.
    """
    records = tuple(records)
    steps = tuple(row["step"] for row in records)
    channels = {}
    for channel, field, direction in (
        ("entropy", "h_n_latest", "lower"),
        ("g", "g", "upper"),
        ("L", "L_t", "lower"),
    ):
        parameters = constants[channel]
        channels[channel] = channel_cusum(
            steps,
            tuple(row[field] for row in records),
            reference=parameters["reference"],
            allowance=parameters["allowance"],
            threshold=parameters["threshold"],
            direction=direction,
        )
    heartbeats = []
    alarm_records = []
    operational_alarm_steps = []
    for i, step in enumerate(steps):
        heartbeats.append({
            "record_type": "heartbeat",
            "step": step,
            "heartbeat_counter": i + 1,
            "S_H": channels["entropy"]["statistics"][i],
            "S_g": channels["g"]["statistics"][i],
            "S_L": channels["L"]["statistics"][i],
        })
        for channel in ("entropy", "g", "L"):
            if channels[channel]["alarms"][i]:
                alarm_records.append({
                    "record_type": "alarm",
                    "step": step,
                    "channel": channel,
                    "statistic_before_reset": channels[channel]["candidate_statistics"][i],
                    "statistic_after_reset": channels[channel]["statistics"][i],
                    "operational_channel": channel in ("entropy", "g"),
                })
        if channels["entropy"]["alarms"][i] or channels["g"]["alarms"][i]:
            operational_alarm_steps.append(step)
    return {
        "channels": channels,
        "heartbeats": tuple(heartbeats),
        "alarm_records": tuple(alarm_records),
        "operational_alarm_steps": tuple(operational_alarm_steps),
        "first_operational_alarm_step": operational_alarm_steps[0] if operational_alarm_steps else None,
    }
