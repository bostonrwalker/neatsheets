import re
from enum import Enum


class Keystroke(Enum):
    """ Map representations in data file to key names """
    BACKSPACE = '⌫'
    CMD = '⌘'
    CTRL = '^'
    DEL = 'del'
    END = 'end'
    ESC = 'esc'
    FN = 'fn'
    HOME = 'home'
    OPT = '⌥'
    PGDN = 'pgdn'
    PGUP = 'pgup'
    RET = '⏎'
    SHIFT = '⇧'
    SPACE = 'space'
    TAB = 'tab'
    UP = '↑'
    DOWN = '↓'
    LEFT = '←'
    RIGHT = '→'
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'
    F6 = 'F6'
    F7 = 'F7'
    F8 = 'F8'
    F9 = 'F9'
    F10 = 'F10'
    F11 = 'F11'
    F12 = 'F12'
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    H = 'H'
    I = 'I'
    J = 'J'
    K = 'K'
    L = 'L'
    M = 'M'
    N = 'N'
    O = 'O'
    P = 'P'
    Q = 'Q'
    R = 'R'
    S = 'S'
    T = 'T'
    U = 'U'
    V = 'V'
    W = 'W'
    X = 'X'
    Y = 'Y'
    Z = 'Z'
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    ZERO = '0'
    APOSTROPHE = '\''
    PERIOD = '.'
    QUESTION_MARK = '?'
    SLASH = '/'
    PLUS = '+'
    MINUS = '-'
    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'


class KeystrokeRange:
    """ Class representing a range of possible keystrokes, e.g. 0-9, A-Z """

    def __init__(self, start: Keystroke, end: Keystroke):
        self.__start = start
        self.__end = end

    @property
    def start(self) -> Keystroke:
        return self.__start

    @property
    def end(self) -> Keystroke:
        return self.__end

    def __str__(self) -> str:
        return (f'KeystrokeRange{{'
                f'start={self.__start},'
                f'end={self.__end}}}')

    def __eq__(self, other) -> bool:
        return (type(other) == KeystrokeRange and
                self.__start == other.start and
                self.__end == other.end)

    def __hash__(self) -> int:
        return hash((self.__start, self.__end))


class Shortcut:
    """ Combination of keystrokes """

    def __init__(self, *keystrokes: Keystroke | KeystrokeRange):
        self.__keystrokes = keystrokes

    @property
    def keystrokes(self) -> tuple[Keystroke | KeystrokeRange, ...]:
        return self.__keystrokes

    def __str__(self) -> str:
        return (f'Shortcut{{'
                f'keystrokes={self.__keystrokes}}}')

    def __eq__(self, other) -> bool:
        return (type(other) == Shortcut and
                self.__keystrokes == other.keystrokes)

    def __hash__(self) -> int:
        return hash(self.__keystrokes)

    @staticmethod
    def parse(csv_str: str) -> 'Shortcut':
        """ Parse combination of keystrokes from CSV file as Shortcut """
        keystrokes: list[Keystroke | KeystrokeRange] = []
        for s in csv_str.split():
            try:
                keystrokes.append(Keystroke(s))
            except ValueError as e:
                try:
                    keystrokes.append(KeystrokeRange(*(Keystroke(k) for k in s.split('-'))))
                except ValueError as _:
                    raise e

        return Shortcut(*keystrokes)


class Task:

    def __init__(self, section: str, desc: str, shortcut: tuple[Shortcut, ...], important: bool):
        self.__section = section
        self.__desc = desc
        self.__shortcut = shortcut
        self.__important = important

    @property
    def section(self) -> str:
        return self.__section

    @property
    def desc(self) -> str:
        return self.__desc

    @property
    def shortcut(self) -> tuple[Shortcut, ...]:
        return self.__shortcut

    @property
    def important(self) -> bool:
        return self.__important

    def __str__(self) -> str:
        return (f'Task{{'
                f'section="{self.__section}",'
                f'desc="{self.__desc}",'
                f'shortcut={self.__shortcut},'
                f'important={self.__important}}}')

    def __eq__(self, other) -> bool:
        return (type(other) == Task and
                self.__section == other.section and
                self.__desc == other.desc and
                self.__shortcut == other.shortcut and
                self.__important == other.important)

    def __hash__(self) -> int:
        return hash((self.__section, self.__desc, self.__shortcut, self.__important))

    @staticmethod
    def parse(section: str, desc: str, shortcut: str, important: str) -> 'Task':
        """ Parse columns from CSV file as Task """
        shortcut = tuple(Shortcut.parse(s) for s in re.split(r'\s*,\s*', shortcut))
        important = bool(important)
        return Task(section, desc, shortcut, important)


def test_parse_shortcut() -> None:
    """ Test parse() function """
    assert Shortcut.parse('⌘ S') == Shortcut(Keystroke.CMD, Keystroke.S)
    assert Shortcut.parse('^ 0-8') == Shortcut(Keystroke.CTRL, KeystrokeRange(Keystroke.ZERO, Keystroke.EIGHT))


def test_parse_task() -> None:
    """ Test parse() function """
    assert Task.parse('Navigation', 'Back', '⌘ ←, ⌘ [', 'true') == \
           Task('Navigation',
                'Back',
                (Shortcut(Keystroke.CMD, Keystroke.LEFT), Shortcut(Keystroke.CMD, Keystroke.LEFT_BRACKET)),
                True)
