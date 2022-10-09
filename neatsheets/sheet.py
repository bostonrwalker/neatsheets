from csv import DictReader, DictWriter
from pathlib import Path
from lxml import html

from neatsheets.language import Language
from neatsheets.platform import Platform
from neatsheets.task import Task, Shortcut, Keystroke, KeystrokeRange, KeystrokeSet
from neatsheets.utils import assert_etrees_equal


class Sheet:
    """ Class representing a cheat sheet """

    def __init__(self, language: Language, application: str, platform: Platform, tasks: list[Task]):
        self.__language = language
        self.__application = application
        self.__platform = platform
        self.__tasks = tasks

    @property
    def language(self) -> Language:
        return self.__language

    @property
    def application(self) -> str:
        return self.__application

    @property
    def platform(self) -> Platform:
        return self.__platform

    @property
    def tasks(self) -> list[Task]:
        return self.__tasks

    def __str__(self) -> str:
        return (f'Sheet{{'
                f'language={self.__language},'
                f'application="{self.__application}",'
                f'platform={self.__platform}}}')

    def write_csv(self, path: None | Path = None) -> None:
        """ Write sheet to CSV file """

        path = path or (Path(__file__).parent / 'data' / self.__language.value /
                        f'{self.__application.lower()}_{self.__platform.value}.csv')

        with path.open('w', encoding='UTF-16BE') as csv_file:
            writer = DictWriter(csv_file, ('section', 'desc', 'shortcut', 'important'))
            writer.writeheader()
            for task in self.__tasks:
                writer.writerow(task.to_csv_dict())

    def to_html(self) -> str:
        """ Render sheet as HTML """

        from jinja2 import Environment, PackageLoader, select_autoescape

        # Get list of unique keys while preserving order
        sections = list(dict.fromkeys(task.section for task in self.__tasks))
        tasks = {section: [task for task in self.__tasks if task.section == section] for section in sections}

        env = Environment(loader=PackageLoader('neatsheets', encoding='UTF-16BE'), autoescape=select_autoescape())
        template = env.get_template('sheet_table.html')
        return template.render(sections=sections, tasks=tasks)

    @staticmethod
    def build_sheet(language: Language, application: str, platform: Platform):
        """ Build sheet from a CSV file """

        csv_filename = f'{application.lower()}_{platform.value}.csv'
        csv_path = Path(__file__).parent / 'data' / language.value / csv_filename

        if not csv_path.exists():
            raise ValueError(f'Could not find sheet data for (language: {language}, application: "{application}", '
                             f'platform: {platform})')

        with csv_path.open('r', encoding='utf-16') as csv_file:
            reader = DictReader(csv_file)
            tasks = list(Task.parse(**row) for row in reader)

        return Sheet(language, application, platform, tasks)


def test_build_sheet() -> None:
    """ Test build_sheet() method """
    print(Sheet.build_sheet(Language.EN, 'Firefox', Platform.MAC))


def test_sheet_to_html() -> None:
    """ Test to_html() method """

    sheet = Sheet(Language.EN, 'Windows', Platform.PC, [
        Task('Commands', 'Look around',
             (Shortcut(KeystrokeSet(Keystroke.W, Keystroke.A, Keystroke.S, Keystroke.D)), ), True),
        Task('Commands', 'Create a new workbook', (Shortcut(Keystroke.CTRL, Keystroke.N), ), True),
        Task('Commands', 'Open an existing workbook',
             (Shortcut(Keystroke.CTRL, Keystroke.O), Shortcut(Keystroke.CTRL, Keystroke.BACKSPACE)), True),
        Task('Surprises', 'I dunno',
             (Shortcut(Keystroke.CTRL, KeystrokeRange(Keystroke.ZERO, Keystroke.NINE)), ), True),
    ])

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
