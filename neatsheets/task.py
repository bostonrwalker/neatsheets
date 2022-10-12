import re
from enum import Enum
from typing import Iterator, Any


class Keystroke(Enum):
    """ Map representations in data file to key names """
    BACKSPACE = '⌫'
    CMD = '⌘'
    WINDOWS = '⊞'
    CTRL = '^'
    DEL = 'del'
    END = 'end'
    ESC = 'esc'
    FN = 'fn'
    HOME = 'home'
    OPT = '⌥'
    ALT = 'alt'
    PGDN = 'pgdn'
    PGUP = 'pgup'
    RET = '⏎'
    SHIFT = '⇧'
    SPACE = 'space'
    TAB = 'tab'
    SCROLL_LOCK = 'scroll\xa0lock'
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
    BACKTICK = '`'
    PERIOD = '.'
    COMMA = ','
    SEMICOLON = ';'
    QUESTION_MARK = '?'
    SLASH = '/'
    PLUS = '+'
    MINUS = '-'
    EQUALS = '='
    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'
    MOUSE_SCROLL = '⇳'


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

    @property
    def value(self) -> str:
        """ Format for display / storage in CSV, same as Keystroke enum """
        return f'{self.__start.value}-{self.__end.value}'

    def __str__(self) -> str:
        return (f'KeystrokeRange{{'
                f'start={self.__start},'
                f'end={self.__end}}}')

    def __eq__(self, other: Any) -> bool:
        return (type(other) == KeystrokeRange and
                self.__start == other.start and
                self.__end == other.end)

    def __hash__(self) -> int:
        return hash((self.__start, self.__end))


class KeystrokeSet:
    """ Class representing a set of possible keystrokes, e.g. '↑, ↓, ←, or →'"""

    def __init__(self, *keystrokes: Keystroke):
        self.__keystrokes = keystrokes

    @property
    def keystrokes(self) -> tuple[Keystroke]:
        return self.__keystrokes

    @property
    def value(self) -> str:
        """ Format for display / storage in CSV, same as Keystroke enum """
        return ''.join(k.value for k in self.__keystrokes)

    def __str__(self) -> str:
        return (f'KeystrokeSet{{'
                f'keystrokes={self.__keystrokes}}}')

    def __eq__(self, other: Any) -> bool:
        return (type(other) == KeystrokeSet and
                self.__keystrokes == other.keystrokes)

    def __hash__(self) -> int:
        return hash(self.__keystrokes)


class Shortcut:
    """ Combination of keystrokes """

    def __init__(self, *keystrokes: Keystroke | KeystrokeRange | KeystrokeSet):
        self.__keystrokes = keystrokes

    @property
    def keystrokes(self) -> tuple[Keystroke | KeystrokeRange | KeystrokeSet, ...]:
        return self.__keystrokes

    def to_csv_str(self) -> str:
        """ Format for storage in CSV file """
        return ' '.join(k.value for k in self.__keystrokes)

    def __str__(self) -> str:
        return (f'Shortcut{{'
                f'keystrokes={self.__keystrokes}}}')

    def __eq__(self, other) -> bool:
        return (type(other) == Shortcut and
                self.__keystrokes == other.keystrokes)

    def __hash__(self) -> int:
        return hash(self.__keystrokes)

    def __iter__(self) -> Iterator[Keystroke | KeystrokeRange | KeystrokeSet]:
        return iter(self.__keystrokes)

    @staticmethod
    def parse(csv_str: str) -> 'Shortcut':
        """ Parse combination of keystrokes from CSV file as Shortcut """
        keystrokes: list[Keystroke | KeystrokeRange | KeystrokeSet] = []
        for s in csv_str.split(' '):
            try:
                keystrokes.append(Keystroke(s))
            except ValueError as e:
                try:
                    keystrokes.append(KeystrokeRange(*(Keystroke(k) for k in s.split('-'))))
                except ValueError as _:
                    try:
                        keystrokes.append(KeystrokeSet(*(Keystroke(k) for k in s)))
                    except ValueError as _:
                        raise e

        return Shortcut(*keystrokes)


class Task:

    def __init__(self, desc: str, shortcut: tuple[Shortcut, ...], important: bool):
        self.__desc = desc
        self.__shortcut = shortcut
        self.__important = important

    @property
    def desc(self) -> str:
        return self.__desc

    @property
    def shortcut(self) -> tuple[Shortcut, ...]:
        return self.__shortcut

    @property
    def important(self) -> bool:
        return self.__important

    def to_csv_dict(self) -> dict[str, str]:
        return {
            'desc': self.__desc,
            'shortcut': ', '.join(s.to_csv_str() for s in self.__shortcut),
            'important': 'true' if self.__important else 'false',
        }

    def __str__(self) -> str:
        return (f'Task{{'
                f'desc="{self.__desc}",'
                f'shortcut={self.__shortcut},'
                f'important={self.__important}}}')

    def __eq__(self, other: Any) -> bool:
        return (type(other) == Task and
                self.__desc == other.desc and
                self.__shortcut == other.shortcut and
                self.__important == other.important)

    def __hash__(self) -> int:
        return hash((self.__desc, self.__shortcut, self.__important))

    @staticmethod
    def parse(desc: str, shortcut: str, important: str) -> 'Task':
        """ Parse columns from CSV file as Task """
        shortcut = tuple(Shortcut.parse(s) for s in re.split(r'\s*,\s*', shortcut))
        important = important.lower() == 'true'
        return Task(desc, shortcut, important)


def test_parse_shortcut() -> None:
    """ Test parse() function """
    assert Shortcut.parse('⌘ S') == Shortcut(Keystroke.CMD, Keystroke.S)
    assert Shortcut.parse('^ 0-8') == Shortcut(Keystroke.CTRL, KeystrokeRange(Keystroke.ZERO, Keystroke.EIGHT))
    assert Shortcut.parse('scroll\xa0lock') == Shortcut(Keystroke.SCROLL_LOCK)
    assert Shortcut.parse('↑↓←→') == Shortcut(KeystrokeSet(Keystroke.UP, Keystroke.DOWN, Keystroke.LEFT,
                                                           Keystroke.RIGHT))


def test_parse_task() -> None:
    """ Test parse() function """
    assert Task.parse('Back', '⌘ ←, ⌘ [', 'true') == \
           Task('Back',
                (Shortcut(Keystroke.CMD, Keystroke.LEFT), Shortcut(Keystroke.CMD, Keystroke.LEFT_BRACKET)),
                True)
    assert Task.parse('Scroll Lock', 'scroll\xa0lock', 'false') == \
           Task('Scroll Lock',
                (Shortcut(Keystroke.SCROLL_LOCK), ),
                False)
