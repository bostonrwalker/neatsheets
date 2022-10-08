from lxml import etree

from neatsheets.language import Language


def assert_etrees_equal(actual: etree, expected: etree) -> None:
    """ Assert equality of two lxml element trees """
    # https://stackoverflow.com/questions/7905380/testing-equivalence-of-xml-etree-elementtree
    assert actual.tag == expected.tag, \
        f'Expected tag: {repr(expected.tag)}, actual tag: {repr(actual.tag)}'
    assert actual.text == expected.text, \
        f'Expected text: {repr(expected.text)}, actual text: {repr(actual.text)}'
    assert actual.tail == expected.tail, \
        f'Expected tail: {repr(expected.tail)}, actual tail: {repr(actual.tail)}'
    assert actual.attrib == expected.attrib, \
        f'Expected attrib: {expected.attrib}, actual attrib: {actual.attrib}'
    assert len(actual) == len(expected), \
        f'Expected len: {len(expected)}, actual len: {len(actual)}'
    for elem_actual, elem_expected in zip(actual, expected):
        assert_etrees_equal(elem_actual, elem_expected)


_titlecase_exceptions = {
    Language.EN: [
        # Conjunctions
        'and', 'as', 'but', 'for', 'if', 'nor', 'or', 'so', 'yet',
        # Articles
        'a', 'an', 'the',
        # Prepositions
        'as', 'at', 'by', 'for', 'in', 'of', 'off', 'on', 'per', 'to', 'up', 'via',
    ]
}


def titlecase(title: str, language: Language = Language.EN) -> str:
    """ Titlecase a sentence (i.e. capitalize all words except for conjunctions, articles, and prepositions """
    # https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case

    if language not in _titlecase_exceptions:
        raise ValueError(f'Language not implemented: {language}')

    exceptions = _titlecase_exceptions[language]

    words = title.split()
    assert len(words) >= 1

    words = [words[0].capitalize()] + [word.capitalize() if not word in exceptions else word for word in words[1:]]

    return ' '.join(words)
