from collections import defaultdict
from csv import DictReader, DictWriter
from pathlib import Path
from typing import Mapping

from lxml import html

from neatsheets.task import Task, Shortcut, Keystroke, KeystrokeRange, KeystrokeSet
from neatsheets.utils import assert_etrees_equal


class Sheet:
    """ Class representing a cheat sheet """

    def __init__(self, tasks: Mapping[str, list[Task]]):
        self.__tasks = tasks

    @property
    def tasks(self) -> Mapping[str, list[Task]]:
        return self.__tasks

    def __str__(self) -> str:
        return (f'Sheet{{'
                f'tasks={self.__tasks}}}')

    def write_csv(self, path: Path) -> None:
        """ Write sheet to CSV file """

        with path.open('w', encoding='UTF-16BE') as csv_file:
            writer = DictWriter(csv_file, ('section', 'desc', 'shortcut', 'important'))
            writer.writeheader()
            for section in self.__tasks:
                for task in self.__tasks[section]:
                    writer.writerow({
                        'section': section,
                        **task.to_csv_dict()
                    })

    def to_html(self) -> str:
        """ Render sheet as HTML """

        from jinja2 import Environment, PackageLoader, select_autoescape

        env = Environment(loader=PackageLoader('neatsheets', encoding='UTF-16'), autoescape=select_autoescape())
        template = env.get_template('sheet.html')
        return template.render(tasks=self.tasks)

    @staticmethod
    def from_csv(csv_path: Path) -> 'Sheet':
        """ Build sheet from a CSV file """

        tasks = defaultdict(list)

        with csv_path.open('r', encoding='utf-16') as csv_file:
            reader = DictReader(csv_file)
            for row in reader:
                section = row.pop('section')
                task = Task.parse(**row)
                tasks[section].append(task)

        return Sheet(tasks)


def test_build_sheet() -> None:
    """ Test build_sheet() method """
    print(Sheet.from_csv(Path(__file__).parent / 'static' / 'apps' / 'en' / 'firefox' / 'firefox_mac.csv'))


def test_sheet_to_html() -> None:
    """ Test to_html() method """

    sheet = Sheet({
        'Commands': [
            Task('Look around', (Shortcut(KeystrokeSet(Keystroke.W, Keystroke.A, Keystroke.S, Keystroke.D)), ), True),
            Task('Create a new workbook', (Shortcut(Keystroke.CTRL, Keystroke.N), ), True),
            Task('Open an existing workbook',
                 (Shortcut(Keystroke.CTRL, Keystroke.O), Shortcut(Keystroke.CTRL, Keystroke.BACKSPACE)), True),
        ],
        'Surprises': [
            Task('I dunno', (Shortcut(Keystroke.CTRL, KeystrokeRange(Keystroke.ZERO, Keystroke.NINE)), ), True),
        ],
    })

    expected = """<h2>Commands</h2>
<table>
    <tbody>
        <tr>
            <td>
                Look around
            </td>
            <td>
                <span class="key">W</span>
                <span class="key">A</span>
                <span class="key">S</span>
                <span class="key">D</span>
                <br>
            </td>
        </tr>
        <tr>
            <td>
                Create a new workbook
            </td>
            <td>
                <span class="key">^</span>
                 + 
                <span class="key">N</span>
                <br>
            </td>
        </tr>
        <tr>
            <td>
                Open an existing workbook
            </td>
            <td>
                <span class="key">^</span>
                 + 
                <span class="key">O</span>
                <br>
                <span class="key">^</span>
                 + 
                <span class="key">⌫</span>
                <br>
            </td>
        </tr>
    </tbody>
</table>
<h2>Surprises</h2>
<table>
    <tbody>
        <tr>
            <td>
                I dunno
            </td>
            <td>
                <span class="key">^</span>
                 + 
                <span class="key">0</span>
                 to
                <span class="key">9</span>
                <br>
            </td>
        </tr>
    </tbody>
</table>
"""

    assert_etrees_equal(html.fromstring(sheet.to_html()), html.fromstring(expected))
