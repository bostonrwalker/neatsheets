from collections import defaultdict
from pathlib import Path
from typing import Mapping, MutableMapping, Iterable

import tomli

from neatsheets.language import Language
from neatsheets.platform import Platform
from neatsheets.sheet import Sheet


class App:
    """ Class to represent the collective data for a single app """

    def __init__(self, logo: Path, display_name: str, display_name_full: str, sheets: Mapping[Platform, Sheet]):
        self.__logo = logo
        self.__display_name = display_name
        self.__display_name_full = display_name_full
        self.__sheets = sheets

    @property
    def logo(self) -> Path:
        return self.__logo

    @property
    def display_name(self) -> str:
        return self.__display_name

    @property
    def display_name_full(self) -> str:
        return self.__display_name_full

    @property
    def sheets(self) -> Mapping[Platform, Sheet]:
        return self.__sheets

    @property
    def platforms(self) -> Iterable[Platform]:
        return self.__sheets.keys()

    def to_html(self) -> str:
        """ Render app as HTML Neatsheet """

        from jinja2 import Environment, PackageLoader, select_autoescape

        env = Environment(loader=PackageLoader('neatsheets', encoding='UTF-16BE'), autoescape=select_autoescape())
        template = env.get_template('app.html')
        return template.render(app=self, platform=Platform.PC)

    @staticmethod
    def from_path(path: Path) -> 'App':
        """ Load app data from a path """

        config_path = path / 'app.toml'
        with config_path.open('rb') as config_file:
            config = tomli.load(config_file)

        logo = path / config['logo']
        display_name = config['display_name']
        display_name_full = config['display_name_full']

        sheets = {}
        for platform in Platform:
            if platform.value.lower() in config:
                platform_config = config[platform.value.lower()]
                data_path = path / platform_config['data']
                sheets[platform] = Sheet.from_csv(data_path)

        return App(logo, display_name, display_name_full, sheets)


class AppManager:
    """ Class to manage loading of App objects from file """

    __instance: 'AppManager' = None
    @staticmethod
    def get_instance():
        if AppManager.__instance is None:
            AppManager.__instance = AppManager()

        return AppManager.__instance

    def __init__(self, path: None | Path = None):
        self.__path = path or Path(__file__).parent / 'static' / 'apps'
        self.__apps: MutableMapping[Language, MutableMapping[str, App]] = defaultdict(dict)

    @property
    def path(self) -> Path:
        return self.__path

    def load_all(self):
        for language_path in [p for p in self.path.iterdir() if p.is_dir() and not p.name.startswith('.')]:
            language = Language(language_path.name)
            for app_path in [p for p in language_path.iterdir() if p.is_dir() and not p.name.startswith('.')]:
                app_name = app_path.name
                self.__apps[language][app_name] = App.from_path(app_path)

    def get_app(self, language: Language, app_name: str) -> App:
        return self.__apps[language][app_name]


def test_from_path() -> None:
    """ Test loading from path """
    print(App.from_path(Path(__file__).parent / 'static' / 'apps' / 'en' / 'excel'))


def test_load_all() -> None:
    """ Test loading all apps from path """
    AppManager.get_instance().load_all()
