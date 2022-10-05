from csv import DictReader
from enum import Enum
from pathlib import Path

from neatsheets.task import Task


class Language(Enum):
    EN = 'en'
    FR = 'fr'


class Platform(Enum):
    MAC = 'mac'
    PC = 'pc'


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

    @staticmethod
    def build_sheet(language: Language, application: str, platform: Platform):
        """ Build sheet from a CSV file """

        csv_filename = f'{application.lower()}_{platform.value}.csv'
        csv_path = Path(__file__).parent.parent / 'resources' / 'shortcuts' / language.value / csv_filename

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
