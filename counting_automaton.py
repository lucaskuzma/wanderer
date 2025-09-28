from dataclasses import dataclass
import operator


@dataclass
class State:
    counter: int
    threshold: int
    operator: str
    operand: int

    def __hash__(self):
        return hash((self.counter, self.threshold, self.operator, self.operand))


class CountingAutomaton:
    """
    State machine that applies an operator and operand to a value at each step, and transitions to a new state when the current state's counter reaches a threshold.
    """

    def __init__(self):
        self.ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
        }
        self.states = [
            State(
                counter=0,
                threshold=1,
                operator="+",
                operand=1,
            ),
            State(
                counter=0,
                threshold=2,
                operator="-",
                operand=1,
            ),
            State(
                counter=0,
                threshold=1,
                operator="+",
                operand=5,
            ),
            State(
                counter=0,
                threshold=1,
                operator="-",
                operand=2,
            ),
        ]
        self.current_state = self.states[0]
        self.transition_matrix = {
            self.states[0]: self.states[1],
            self.states[1]: self.states[2],
            self.states[2]: self.states[3],
            self.states[3]: self.states[0],
        }
        self.value = 0

    def apply_op(self, op):
        return self.ops[op](self.value, self.current_state.operand)

    def step(self):
        self.current_state.counter += 1
        if self.current_state.counter >= self.current_state.threshold:
            self.current_state.counter = 0
            self.current_state = self.transition_matrix[self.current_state]
        self.value = self.apply_op(self.current_state.operator)
        return self.value


if __name__ == "__main__":
    sm = CountingAutomaton()
    for _ in range(120):
        print("-" * (sm.value % 32))
        sm.step()
