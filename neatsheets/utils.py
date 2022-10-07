from lxml import etree


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
