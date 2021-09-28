# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import random
import itertools
import sys

class Automaton:
    def __init__(self, atype=None, states=None, alphabet=None, instructions=None, initial_states=None):
        self.atype = type
        self.__states = set()
        self.__alphabet = set()
        if not instructions:
            self.__instructions = {}
        else:
            self.__instructions = instructions
        self.__initial_states = set()
        self.__curr_state = None
        self._tape = ''
        self._position = -1

    @property
    def alphabet(self):
        return self.__alphabet

    @alphabet.setter
    def alphabet(self, abet):
        self.__alphabet = set(abet)

    @property
    def initial_states(self):
        return self.__initial_states

    def set_initial_state(self, state):
        if state not in self.states:
            self.__states.add(state)
        self.__initial_states = {state}

    @initial_states.setter
    def initial_states(self, states):
        # states should be a set
        if not states <= self.__states:
            self.__states = self.__states | states
        self.__initial_states = states

    @property
    def states(self) -> set:
        return self.__states

    @states.setter
    def states(self, states):
        self.__states = set(states)

    def add_instruction(self, left, right):
        self.__instructions[left] = right

    @property
    def instructions(self):
        return self.__instructions

    @instructions.setter
    def instructions(self, instructions):
        self.__instructions = instructions

    @property
    def state(self):
        return self.__curr_state

    @state.setter
    def state(self, state):
        self.__curr_state = state

    def step(self):
        pass

    @property
    def configuration(self):
        return self.__curr_state, self._tape, self._position

    @configuration.setter
    def configuration(self, conf):
        if conf[0] not in self.__states:
            raise f"Wrong configuration {conf} - unknown state"
        self.__curr_state = conf[0]
        self._tape = conf[1]
        self._position = conf[2]


class nrNFAwtl(Automaton):
    def __init__(self, atype="nrNFAwtl", states=None, alphabet=None, instructions=None, initial_states=None):
        super().__init__(type, states, alphabet, instructions, initial_states)
        if instructions is None:
            instructions = {}
        if alphabet is None:
            alphabet = set()
        self._endmarker = '$'
        self.__transparency = {}
        if states:
            for st in states:
                self.__transparency[st] = set()

    @property
    def transparency(self) -> dict:
        return self.__transparency

    @transparency.setter
    def transparency(self, states_transparency):
        self.__transparency = states_transparency

    def step(self):
        while self._tape[self._position] in self.transparency[self.state]:
            self._position += 1
        symbol = self._tape[self._position]
        if symbol not in self.alphabet and symbol != self._endmarker:
            raise Exception(f"Symbol {symbol} is not in the automaton's alphabet")
        if (self.state, symbol) not in self.instructions:
            return "Reject"
        self.state = one_of(self.instructions[(self.state, symbol)])
        if self._tape[self._position] == self._endmarker:
            self._position = 0
        else:
            self._tape = self._tape[:self._position] + self._tape[self._position + 1:]
        return self.state

    def next_configs(self, state, tape, position):
        while tape[position] in self.transparency[state]:
            position += 1
        symbol = tape[position]
        if symbol not in self.alphabet and symbol != self._endmarker:
            raise Exception(f"Symbol {symbol} is not in the automaton's alphabet")
        if (state, symbol) not in self.instructions:
            return []
        next_states = self.instructions[(state, symbol)]
        if tape[position] == self._endmarker:
            next_position = 0
            next_tape = tape
        else:
            next_position = position
            next_tape = tape[:position] + tape[position + 1:]

        return [(st, next_tape, next_position) for st in next_states]

    def accepts_from_configuration(self, state, tape, position):
        if state == 'Accept':
            return True
        next_configs = self.next_configs(state, tape, position)
        for c in next_configs:
            if self.accepts_from_configuration(c[0], c[1], c[2]):
                return True
        return False

    def accepts(self, word):
        orig_recursion_limit = sys.getrecursionlimit()
        tape = word + self._endmarker
        if len(tape) > orig_recursion_limit + 20:
            sys.setrecursionlimit(len(tape) + 20)
        for state in self.initial_states:
            if self.accepts_from_configuration(state, tape, 0):
                if sys.getrecursionlimit() > orig_recursion_limit:
                    sys.setrecursionlimit(orig_recursion_limit)
                return True
        if sys.getrecursionlimit() > orig_recursion_limit:
            sys.setrecursionlimit(orig_recursion_limit)
        return False


def one_of(state_set):
    if not state_set:
        return None
    else:
        return random.choice(list(state_set))


def accepted_words(aut, max_len):
    res = []
    for l in range(max_len + 1):
        for w in itertools.product(aut.alphabet, repeat=l):
            word = ''.join(w)
            if aut.accepts(word):
                res.append(word)
    return res


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    aut = nrNFAwtl('nrNFAwtl')
    aut.alphabet = ['a', 'b', 'c']
    aut.states = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'qI', 'qI\'']
    aut.transparency = {'q0': {'a', 'c'}, 'q1': set(), 'q2': {'a', 'b'},
                        'q3': set(), 'q4': {'b', 'c'}, 'q5': set(),
                        'q6': {'c'}, 'q7': {'a'}, 'q8': {'b'},
                        'q9': {'c'}, 'q10': set(), 'q11': set(), 'qI': {'a'}, 'qI\'': set()}
    aut.set_initial_state('qI')
    print("Alphabet:", aut.alphabet)
    print("Set of states:", aut.states)
    print("Initial states:", aut.initial_states)

    aut.state = 'qI'
    print("Current state:", aut.state)

    aut.add_instruction(('qI', 'b'), {'q1'})
    aut.add_instruction(('qI', '$'), {'qI\''})
    aut.add_instruction(('qI\'', '$'), {'Accept'})
    aut.add_instruction(('q0', 'b'), {'q1'})
    aut.add_instruction(('q0', '$'), {'q6'})
    aut.add_instruction(('q1', 'c'), {'q2'})
    aut.add_instruction(('q2', 'c'), {'q3'})
    aut.add_instruction(('q2', '$'), {'q10'})
    aut.add_instruction(('q3', 'a'), {'q4'})
    aut.add_instruction(('q4', 'a'), {'q5'})
    aut.add_instruction(('q5', 'b'), {'q0'})
    aut.add_instruction(('q6', 'a'), {'q7'})
    aut.add_instruction(('q6', '$'), {'Accept'})
    aut.add_instruction(('q7', 'b'), {'q8'})
    aut.add_instruction(('q8', 'c'), {'q9'})
    aut.add_instruction(('q9', 'a'), {'q7'})
    aut.add_instruction(('q9', '$'), {'q0'})
    aut.add_instruction(('q10', 'a'), {'q11'})
    aut.add_instruction(('q11', '$'), {'Accept'})

    aut.configuration = ('qI', 'abc$', 0)

    state = aut.configuration[0]
    print(aut.configuration)
    while state != 'Reject' and state != 'Accept':
        state = aut.step()
        print(aut.configuration)

    print("End of computation:", state)

    aut.configuration = ('qI', 'abcabcabcabc$', 0)

    state = aut.configuration[0]
    print(aut.configuration)
    while state != 'Reject' and state != 'Accept':
        state = aut.step()
        print(aut.configuration)

    print('End of computation:', state)

    print('-------------------')

    print(aut.accepts('abc'))

    print(accepted_words(aut, 15))

    print('-------------------')
    print('Accepted numbers of repeats of "abc"')

    for k in range(1100):
        w = 'abc' * k
        if aut.accepts(w):
            print(k)

    print('-------------------------------')
    print('-- another example automaton --')
    print('-------------------------------')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
