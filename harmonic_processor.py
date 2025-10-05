import math
from counting_automaton import CountingAutomaton


class HarmonicProcessor:
    """
    Processor that applies a harmonic to a note using a counting automaton. The counting automaton is used to determine the harmonic to apply.
    """

    def __init__(self, n_harmonics=8):
        self.n_harmonics = n_harmonics
        self.harmonics = [
            int(round(12 * math.log2(n), 2)) for n in range(1, n_harmonics + 1)
        ]
        self.automaton = CountingAutomaton()
        self.index = 0

    def process(self, note):
        self.index = self.automaton.step() % self.n_harmonics
        delta = self.harmonics[self.index]
        return delta + note

    def __str__(self):
        str_parts = []
        for i, h in enumerate(self.harmonics):
            if i == self.index:
                str_parts.append(f"[{h:02d}]")
            else:
                str_parts.append(f" {h:02d} ")
        return f" {self.automaton} | " + "".join(str_parts)
