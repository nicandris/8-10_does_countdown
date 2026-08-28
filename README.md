# 8-10_does_countdown

8 Out of 10 Cats Does Countdown numbers-round solver.

Exhaustive depth-first search over every pair and operator, so it finds an
exact solution whenever one exists — including solutions that use only some of
the six numbers — and otherwise reports the closest reachable value. A full
search of a six-number game takes about 0.1s.

```
python script.py 25 50 75 100 3 6 952   # one shot
python script.py                        # interactive prompts
python test_solver.py                   # tests
```

![Alt Text](/assets/preview.png)
