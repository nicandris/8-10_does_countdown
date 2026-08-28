"""8 Out of 10 Cats Does Countdown numbers solver.

Exhaustive depth-first search over every pair/operator combination, so it
finds an exact solution if one exists (or the closest reachable value if not),
including solutions that use only some of the numbers.

    python script.py 25 50 75 100 3 6 952
    python script.py                        # interactive
    python script.py --test                 # self-check
"""
import sys
import time


def solve(numbers, target):
    """Return (value, steps) for the best reachable value. Exact match ends the search."""
    best = None
    seen_states = set()

    def consider(value, steps):
        nonlocal best
        if best is None or abs(value - target) < abs(best[0] - target) or (
            abs(value - target) == abs(best[0] - target) and len(steps) < len(best[1])
        ):
            best = (value, steps)
        return value == target

    def search(items):
        # items: list of (value, steps) — steps is the working that produced value
        state = tuple(sorted(v for v, _ in items))
        if state in seen_states:
            return False
        seen_states.add(state)

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, sa = items[i]
                b, sb = items[j]
                if a < b:
                    (a, sa), (b, sb) = (b, sb), (a, sa)
                rest = [items[k] for k in range(len(items)) if k != i and k != j]
                history = sa + sb

                candidates = [(a + b, '+'), (a * b, '*')] if b != 1 else [(a + b, '+')]
                if a != b:
                    candidates.append((a - b, '-'))
                if b != 1 and a % b == 0:
                    candidates.append((a // b, '/'))

                for value, op in candidates:
                    steps = history + (f"{a} {op} {b} = {value}",)
                    if consider(value, steps):
                        return True
                    if rest and search(rest + [(value, steps)]):
                        return True
        return False

    for n in numbers:
        if consider(n, ()):
            return best
    search([(n, ()) for n in numbers])
    return best


def report(numbers, target, value, steps, elapsed):
    lines = [
        '----------------------',
        f"{numbers} : {target}",
        '----------------------',
        *steps,
        '',
        f"Result: {value}" + ('' if value == target else f" (off by {abs(value - target)})"),
        f"Solved in {elapsed:.3f}s",
        '----------------------',
    ]
    return '\n'.join(lines) + '\n'


def test():
    value, steps = solve([25, 50, 75, 100, 3, 6], 952)
    assert value == 952, value
    assert len(steps) == 5, steps
    # Uses a subset: the old random solver could never find these.
    value, steps = solve([1, 2, 3, 4, 5, 6], 11)
    assert (value, len(steps)) == (11, 1), (value, steps)
    # Unreachable target -> closest value, not a crash.
    value, _ = solve([1, 1, 1, 1, 1, 1], 999)
    assert value == 9, value  # (1+1+1) * (1+1+1)
    # 831 is provably unreachable from this set: expect the nearest value, 830.
    t0 = time.perf_counter()
    assert solve([1, 3, 7, 10, 25, 50], 831)[0] == 830
    print(f"OK (worst case, full search: {time.perf_counter() - t0:.3f}s)")


if __name__ == '__main__':
    if '--test' in sys.argv:
        test()
        sys.exit()

    args = [int(a) for a in sys.argv[1:]]
    if args:
        *numbers, target = args
    else:
        numbers = [int(input("Enter number: ")) for _ in range(6)]
        target = int(input("Enter the result: "))

    t0 = time.perf_counter()
    value, steps = solve(numbers, target)
    output = report(numbers, target, value, steps, time.perf_counter() - t0)
    print('\n' + output)
    with open('./logfile.txt', 'a') as logfile:
        logfile.write('\n' + output)
