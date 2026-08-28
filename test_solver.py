"""Tests for the Countdown solver: python3 test_solver.py (or pytest)."""
import json
import pathlib
import time

from script import solve

GAMES = json.loads((pathlib.Path(__file__).parent / 'games.json').read_text())


def brute_force(numbers):
    """Every value reachable from any subset. No pruning, no dedup — the oracle."""
    reached = set(numbers)
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i == j:
                continue
            a, b = numbers[i], numbers[j]
            rest = tuple(numbers[k] for k in range(len(numbers)) if k != i and k != j)
            values = [a + b, a * b]
            if a - b > 0:
                values.append(a - b)
            if b and a % b == 0:
                values.append(a // b)
            for value in values:
                reached |= brute_force(rest + (value,))
    return reached


def reachable_by_subset(numbers):
    """Second oracle: bottom-up over every subset, the opposite direction to the solver."""
    size = len(numbers)
    values = [set() for _ in range(1 << size)]
    for i, number in enumerate(numbers):
        values[1 << i] = {number}
    for mask in range(1, 1 << size):
        if mask & (mask - 1) == 0:
            continue  # a single number, already seeded
        out = values[mask]
        sub = (mask - 1) & mask
        while sub:
            other = mask ^ sub
            if sub < other:  # look at each split once
                for x in values[sub]:
                    for y in values[other]:
                        lo, hi = (y, x) if x > y else (x, y)
                        out.add(hi + lo)
                        out.add(hi * lo)
                        if hi - lo > 0:
                            out.add(hi - lo)
                        if lo and hi % lo == 0:
                            out.add(hi // lo)
            sub = (sub - 1) & mask
    return set().union(*values)


def check_working(numbers, value, steps):
    """Replay the printed working: every step must consume real numbers and add up."""
    pool = list(numbers)
    for line in steps:
        lhs, rhs = line.split(' = ')
        a, op, b = lhs.split()
        a, b, result = int(a), int(b), int(rhs)
        for operand in (a, b):
            assert operand in pool, f"{line}: {operand} is not available in {pool}"
            pool.remove(operand)
        expected = {'+': a + b, '-': a - b, '*': a * b, '/': a / b}[op]
        assert expected == result, f"{line}: should be {expected}"
        assert result > 0, f"{line}: Countdown forbids zero and negatives"
        pool.append(result)
    assert value in pool, f"final value {value} was never produced by {steps}"
    if steps:
        assert int(steps[-1].split(' = ')[1]) == value, "last step must produce the answer"


def test_known_games():
    for numbers, target in [
        ([25, 50, 75, 100, 3, 6], 952),
        ([100, 75, 2, 1, 4, 8], 683),
        ([50, 100, 4, 2, 2, 4], 203),
        ([25, 4, 9, 7, 3, 7], 881),
        ([75, 50, 2, 3, 8, 7], 316),
    ]:
        value, steps = solve(numbers, target)
        assert value == target, f"{numbers} -> {target} missed, got {value}"
        check_working(numbers, value, steps)


def test_uses_a_subset_when_that_is_enough():
    value, steps = solve([1, 2, 3, 4, 5, 6], 11)
    assert (value, len(steps)) == (11, 1), (value, steps)
    # 848 is reachable from these six only by leaving one number unused.
    value, steps = solve([1, 3, 7, 10, 25, 50], 848)
    assert value == 848
    check_working([1, 3, 7, 10, 25, 50], value, steps)


def test_target_already_on_the_board():
    assert solve([25, 50, 75, 100, 3, 6], 75) == (75, ())


def test_unreachable_target_returns_the_closest():
    assert solve([1, 3, 7, 10, 25, 50], 831)[0] == 830
    assert solve([1, 1, 1, 1, 1, 1], 999)[0] == 9  # (1+1+1) * (1+1+1)


def test_division_stays_exact():
    assert solve([3, 100], 33)[0] != 33  # 100/3 is not a whole number, so 33 is out of reach
    value, steps = solve([4, 100], 25)
    assert (value, steps) == (25, ('100 / 4 = 25',))


def test_agrees_with_brute_force():
    for numbers in [(3, 6, 25, 50), (1, 2, 7, 75), (2, 2, 5, 10), (4, 8, 9, 100)]:
        reachable = brute_force(numbers)
        for target in range(1, 400):
            value, steps = solve(list(numbers), target)
            check_working(numbers, value, steps)
            if target in reachable:
                assert value == target, f"{numbers}: missed reachable {target}"
            else:
                assert value != target, f"{numbers}: invented {target}"
                assert abs(value - target) == min(abs(v - target) for v in reachable), (
                    f"{numbers}: {value} is not the closest to {target}"
                )


def test_solves_a_hundred_real_games():
    for numbers, target in GAMES['solvable']:
        value, steps = solve(numbers, target)
        assert value == target, f"{numbers} -> {target}: got {value}"
        check_working(numbers, value, steps)


def test_gets_closest_on_twenty_five_impossible_games():
    for numbers, target, closest in GAMES['unsolvable']:
        value, steps = solve(numbers, target)
        assert value != target, f"{numbers} -> {target} is impossible, but got a match"
        # Ties are real: 834 and 838 are equally good for 836, and score the same.
        assert abs(value - target) == abs(closest - target), (
            f"{numbers} -> {target}: got {value}, no better than {closest} was available"
        )
        check_working(numbers, value, steps)


def test_the_game_table_is_not_taken_on_trust():
    """Re-derive every recorded game with the subset oracle, so the corpus can't rot."""
    for numbers, target in GAMES['solvable']:
        assert target in reachable_by_subset(numbers), f"{numbers} -> {target} is not solvable"
    for numbers, target, closest in GAMES['unsolvable']:
        reachable = reachable_by_subset(numbers)
        assert target not in reachable, f"{numbers} -> {target} is solvable after all"
        assert min(abs(v - target) for v in reachable) == abs(closest - target), (
            f"{numbers} -> {target}: {closest} is not the closest reachable value"
        )


def test_finishes_fast_even_with_no_solution():
    start = time.perf_counter()
    solve([1, 3, 7, 10, 25, 50], 831)
    elapsed = time.perf_counter() - start
    assert elapsed < 2, f"full search took {elapsed:.2f}s"


if __name__ == '__main__':
    for name, case in sorted(globals().items()):
        if name.startswith('test_'):
            start = time.perf_counter()
            case()
            print(f"{name} ok ({time.perf_counter() - start:.2f}s)")
    print("all tests passed")
