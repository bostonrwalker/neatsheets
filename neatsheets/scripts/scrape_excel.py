import re

import requests
from lxml import html
from lxml.etree import ElementBase

from neatsheets.language import Language
from neatsheets.sheet import Sheet, Platform
from neatsheets.task import Keystroke, Shortcut, Task
from neatsheets.utils import titlecase


def scrape_excel_keyboard_shortcuts() -> tuple[Sheet, Sheet]:
    """ Scrape excel keyboard shortcuts and return a Sheet for each platform (PC/Mac) """
    url = 'https://support.microsoft.com/en-us/office/keyboard-shortcuts-in-excel-1798d9d5-842a-42b8-9c99-9b7213f0040f'

    pick_tabs = {Platform.PC: 1, Platform.MAC: 2}

    overrides = {
        'Move Selected Rows, Columns, or Cells': '⇧',
        'Move to the Tell Me or Search Field on the Ribbon and Type a Search Term for Assistance or Help Content':
            'alt+Q',
        'Select the Active Tab on the Ribbon and Activate the Access Keys': 'alt or F10',
        'Open a Context Menu': '⇧+F10 or ⊞',
        'Move From One Group of Controls to Another': '^+←→',
        'Cycle Through Floating Shapes, Such as Text Boxes or Images': '^+alt+5+tab',
        'Scroll Horizontally': '^+⇧+scrollwheel',
        'Insert a Note': '⇧+F2',
        'Insert a Threaded Comment': '^+⇧+F2',
        'Expand Grouped Rows or Columns': '⇧+scrollwheel',
        'Collapse Grouped Rows or Columns': '⇧+scrollwheel',
    }

    keystroke_subs = {
        '\xa0': ' ',
        'COMMAND': '⌘',
        'Windows Menu key': '⊞',
        'Control': '^',
        'Ctrl': '^',
        'The Mac Delete button with a cross symbol on it.': '⌫',
        'Backspace': '⌫',
        'Delete\r\n\t\t\t(not the forward delete key   ⌫ found on full keyboards)': 'del',
        'Delete': 'del',
        'Alt': 'alt',
        'Option': '⌥',
        'Shift': '⇧',
        'Hyphen (-)': '-',
        'Hyphen': '-',
        'Minus sign (-)': '-',
        'Underscore (_)': '-',
        'Equal sign ( = )': '=',
        'Plus sign (+)': '=',
        'Forward slash (/)': '/',
        'Backward slash (\\)': '/',
        'Spacebar': 'space',
        'Return': '⏎',
        'Enter': '⏎',
        'Tab key': 'tab',
        'Tab': 'tab',
        'Esc': 'esc',
        'Scroll lock': 'scroll_lock',
        'Up arrow key': '↑',
        'Down arrow key': '↓',
        'Left arrow key': '←',
        'Right arrow key': '→',
        'Arrow keys': '↑↓←→',
        'Arrow key': '↑↓←→',
        'Home': 'home',
        'Fn': 'fn',
        'End': 'end',
        'Page down': 'pgdn',
        'Page up': 'pgup',
        ', then scroll the mouse wheel up for left, down for right': '+scrollwheel',
        'Semicolon (;)': ';',
        'Colon (:)': ';',
        'Inch mark/Straight double quote (")': '\'',
        'Straight quotation mark (")': '\'',
        'Grave accent (`)': '`',
        'Period (.)': '.',
        'Apostrophe (\')': '\'',
        'Left bracket ([)': '[',
        'Right bracket (])': ']',
        'Left brace ({)': '[',
        'Right brace (})': ']',
        'Left angle bracket (<)': ',',
        'Right angle bracket (>)': '.',
        'Tilde sign (~)': '`',
        'Tilde (~)': '`',
        'Exclamation point (!)': '1',
        'At sign (@)': '2',
        'At symbol (@)': '2',
        'Number sign (#)': '3',
        'Dollar sign ($)': '4',
        'Percent sign (%)': '5',
        'Caret sign (^)': '6',
        'Caret (^)': '6',
        'Ampersand sign (&)': '7',
        'Asterisk sign (*)': '8',
        'Asterisk (*)': '8',
        'Left parenthesis (()': '9',
        'Right parenthesis ())': '0',
        'Zero (0)': '0',
        ', ': '+',  # Parse sequential combinations (e.g. Alt+H, A, C -> alt + H + A + C)
        ' alone': '',
    }

    def _parse_shortcut(text) -> Shortcut:
        try:
            for k_old, k_new in keystroke_subs.items():
                text = text.replace(k_old, k_new)
            keystrokes = tuple(Keystroke(k) for k in text.split('+'))
            return Shortcut(*keystrokes)
        except Exception as e:
            print(e)

    def _parse_row(tr: ElementBase) -> tuple[str, tuple[Shortcut, ...]]:
        td_desc, td_shortcut = tr.xpath('td')
        p_desc = td_desc.xpath('p')[0]
        desc_text = (p_desc.text or '') + ''.join((el.text or '') + (el.tail or '') for el in p_desc.getchildren())
        desc = titlecase(desc_text[:-1])
        if desc in overrides:
            shortcut_text = overrides[desc]
        else:
            shortcut_text = ' '.join(
                ((p.text or '') + ''.join(el.get('alt', '') + (el.tail or '') for el in p.getchildren()))
                for p in td_shortcut.xpath('p'))

        shortcut_text_lines = re.split(r'\s+(?:or|On\sa\sMacBook,)\s+', shortcut_text.strip())
        shortcuts = tuple(_parse_shortcut(line) for line in shortcut_text_lines)
        return desc, shortcuts

    def _parse_list_row(tr: ElementBase) -> list[tuple[str, Shortcut]]:
        list_paras = tr.xpath('td[2]/ul/li/p[1]')
        result: list[tuple[str, Shortcut]] = []
        for p in list_paras:
            text = (p.text or '') + ''.join((el.text or '') + (el.tail or '') for el in p.getchildren())
            if ': ' in text:
                shortcut_text, desc_text = text.split(': ')
            else:
                desc_text = text
                shortcut_text = tr.xpath('td[1]/p')[0].text
            desc = titlecase(desc_text[:-1])
            if desc in overrides:
                shortcut_text = overrides[desc]
            shortcut = _parse_shortcut(shortcut_text)
            result.append((desc, shortcut))

        return result

    def _parse_sheet(content: ElementBase, platform: Platform) -> Sheet:
        tables = content.xpath(f'//div[@id="PickTab-supTabControlContent-{pick_tabs[platform]}"]//section/table')
        tasks = []
        for table in tables:
            section = titlecase(table.xpath('preceding-sibling::*[self::h2 or self::h3]')[0].text)
            rows = table.xpath('tbody/tr')
            if section not in ('Function Keys', 'Other Useful Shortcut Keys'):
                tasks.extend([Task(section, desc, shortcuts, False)
                              for desc, shortcuts in [_parse_row(row) for row in rows]])
            else:
                for row in rows:
                    tasks.extend([Task(section, desc, (shortcut, ), False)
                                  for desc, shortcut in _parse_list_row(row)])

        return Sheet(Language.EN, 'Excel', platform, tasks)

    page = requests.get(url)
    content = html.fromstring(page.content)

    pc_sheet = _parse_sheet(content, Platform.PC)
    mac_sheet = _parse_sheet(content, Platform.MAC)

    return pc_sheet, mac_sheet


if __name__ == '__main__':
    pc_sheet, mac_sheet = scrape_excel_keyboard_shortcuts()
    pc_sheet.write_csv()
    mac_sheet.write_csv()
