from tp1_common import MESSAGES, simulate, show, set_team, load_log, check, score

TEAM = 26


def frame_bits(dlc, ifs=False):
    return 44 + 8 * dlc + (3 if ifs else 0)


def stuff(bits):
    out = []
    last = None
    run = 0
    for b in bits:
        out.append(b)
        if b == last:
            run = run + 1
        else:
            run = 1
        last = b
        if run == 5:
            ins = "0" if b == "1" else "1"
            out.append(ins)
            last = ins
            run = 1
    return "".join(out)


def arbitrate(ids, width=11):
    words = {i: format(i, "0{}b".format(width)) for i in ids}
    alive = set(ids)
    losers = {}
    for pos in range(width):
        if any(words[i][pos] == "0" for i in alive):
            bus = "0"
        else:
            bus = "1"
        for i in list(alive):
            if words[i][pos] != bus:
                losers[i] = pos + 1
                alive.discard(i)
    return alive.pop(), losers


if __name__ == "__main__":
    print("TP 01 - Operation Ghost Bus\n")
    if TEAM is None:
        raise SystemExit("Write your team number at the top of the file:  TEAM = ...")
    set_team(TEAM)

    print(frame_bits(8))
    print(frame_bits(8, ifs=True))
    duration = frame_bits(8) / 500_000 * 1e6
    print(duration)
    check(1, duration)

    print(stuff("1111110"))
    print(stuff("0000001"))
    r = stuff("1000001111100000")
    print(r)
    check(2, r)

    winner, losers = arbitrate([0x2A5, 0x2A1, 0x3A5])
    print(hex(winner))
    for i in losers:
        print(hex(i), "loses at bit", losers[i])
    winner, losers = arbitrate([0x1B3, 0x1A7, 0x1A5])
    print(hex(winner))
    for i in losers:
        print(hex(i), "loses at bit", losers[i])
    check(3, winner)

    load, stats = show("Normal bus, 125 kbit/s", MESSAGES, 125_000)
    check(4, round(100 * load, 2))
    wait = stats[0x500]["max_wait"] * 1e6
    print(wait)
    check(5, round(wait))
    show("Normal bus, 500 kbit/s", MESSAGES, 500_000)

    flood = MESSAGES + [dict(name="Flooder", id=0x000, period=0.001, dlc=8)]
    load_f, stats_f = show("Flooding attack", flood, 125_000)
    check(6, round(100 * load_f))
    flood600 = MESSAGES + [dict(name="Flooder", id=0x600, period=0.001, dlc=8)]
    show("Flooder with id 0x600", flood600, 125_000)
    flood4 = MESSAGES + [dict(name="Flooder", id=0x000, period=0.004, dlc=8)]
    show("Flooder 0x000, period 4 ms", flood4, 125_000)

    log = load_log()
    print(len(log))
    print(log[:3])
    counts = {}
    for time_ms, ident, nbytes in log:
        counts[ident] = counts.get(ident, 0) + 1
    for ident in sorted(counts):
        print(hex(ident), counts[ident])
    expected = {m["id"]: round(3000 / (m["period"] * 1000)) for m in MESSAGES}
    for ident in sorted(expected):
        print(hex(ident), expected[ident], counts.get(ident, 0), counts.get(ident, 0) - expected[ident])
    extra = {i: counts[i] - expected[i] for i in counts if counts[i] != expected.get(i)}
    print(extra)

    check(7, 0x400)
    check(8, 29)

    SPOOFED = 0x400
    PERIOD = 50
    times = [t for t, ident, n in log if ident == SPOOFED]
    alerts = [b for a, b in zip(times, times[1:]) if b - a < PERIOD / 2]
    print(len(alerts))
    print(alerts[:8])

    def phase_alerts(times, period, tol=2.0):
        out = []
        for t in times:
            ph = t % period
            if min(ph, period - ph) > tol:
                out.append(t)
        return out

    better = phase_alerts(times, PERIOD)
    print(len(better), better[:8])

    score()