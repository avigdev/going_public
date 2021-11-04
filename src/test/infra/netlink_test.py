from offline.infra.netlink import NetLink


class MockNetLink(NetLink):
    def __init__(self, entity_filter=lambda x: True):
        self.entity_name = "test"
        self.entity_filter = entity_filter

    def parse_entity(self, ent):
        return ent


def test_parse_entities_empty():
    netlink = MockNetLink()
    x = netlink.parse_entities("")
    assert len(x) == 0


def test_parse_entities_notfound():
    netlink = MockNetLink()
    x = netlink.parse_entities(r"<a></a>")
    assert len(x) == 0


def test_parse_entities_found1():
    netlink = MockNetLink()
    tag = "test"
    attrs = {"q": "blah"}
    searched_entity = r'<test q="blah">'
    entire_doc = f"xxx{searched_entity}"
    x = netlink.parse_entities(entire_doc)
    assert len(x) == 1
    assert x[0].tag == tag
    assert x[0].attrs == attrs


def test_parse_entities_found1_with_closing():
    netlink = MockNetLink()
    tag = "test"
    attrs = {"q": "blah"}
    entire_doc = r'<r\>xxx<test q="blah">yy</test><q>'
    x = netlink.parse_entities(entire_doc)
    assert len(x) == 1
    assert x[0].text == "yy"
    assert x[0].attrs == attrs
    assert x[0].tag == tag


def test_parse_entities_found1_with_nesting():
    netlink = MockNetLink()
    tag = "test"
    attrs = {"q": "blah"}
    entire_doc = r'<r\>xxx<test q="blah"><a>yy</a></test><q\>'
    x = netlink.parse_entities(entire_doc)
    assert len(x) == 1
    assert x[0].text == "yy"
    assert x[0].attrs == attrs
    assert x[0].tag == tag


def test_parse_entities_found_multi():
    netlink = MockNetLink()
    tag = "test"
    entire_doc = r'<test q="blah">a</test>  <test q2="blah2">b</test>'
    x = netlink.parse_entities(entire_doc)
    assert len(x) == 2
    assert x[0].text == "a"
    assert x[1].text == "b"
    assert x[0].attrs == {"q": "blah"}
    assert x[1].attrs == {"q2": "blah2"}
    assert x[0].tag == tag
    assert x[1].tag == tag


def test_parse_entities_filtered():
    netlink = MockNetLink(entity_filter=lambda x: x.text == "a")
    entire_doc = r'<test q="blah">a</test>  <test q2="blah2">b</test>'
    x = netlink.parse_entities(entire_doc)
    assert len(x) == 1
    assert x[0].text == "a"
