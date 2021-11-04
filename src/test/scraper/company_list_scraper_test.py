from offline.scraper.company_list_scraper import EntriesLink, one_page_query
from datetime import datetime
import pytest


class MockEntriesLink(EntriesLink):
    def __init__(self, doc):
        self.doc = doc

    def get(self, url, params):
        return self.doc


def test_one_page_query_extract_date():
    netlink_factory = aEntriesLink()
    netlink = netlink_factory.get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert res[0]["date_issued"] == netlink_factory.datetime


def test_one_page_query_2_identical_filed_tags():
    netlink_factory = aEntriesLink().with_2_identical_filed()
    netlink = netlink_factory.get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert res[0]["date_issued"] == netlink_factory.datetime


def test_one_page_query_2_different_filed_tags():
    netlink = aEntriesLink().with_2_different_filed().get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert "date_issued" not in res[0]


def test_one_page_query_no_filed_tags():
    netlink = aEntriesLink().without_filed().get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert "date_issued" not in res[0]


def test_one_page_query_no_summary_tags():
    netlink = aEntriesLink().without_summary().get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert "date_issued" not in res[0]


def test_one_page_query_two_summary_tags():
    netlink_factory = aEntriesLink().with_two_summary_tags_one_date()
    netlink = netlink_factory.get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert res[0]["date_issued"] == netlink_factory.datetime


def test_one_page_query_filed_exist_but_date_doesnt():
    netlink = aEntriesLink().without_date().get()
    res = one_page_query(netlink, url="", params={})
    assert len(res) == 1
    assert "date_issued" not in res[0]


def test_parse_form_title():
    netlink_factory = aEntriesLink().with_S1A_form_name()
    netlink = netlink_factory.get()
    entire_doc = netlink.get(1, 2)
    entire_entries = netlink._break_to_entities(entire_doc)
    assert len(entire_entries) == 1
    entire_entry = entire_entries[0]
    res = netlink.parse_form_title(entire_entry)
    assert res["form_type"] == "S-1/A", res
    assert res["company_name"] == netlink_factory.company_name, res
    assert f"({res['CIK']})" == netlink_factory.CIK_in_parens, res


def test_parse_form_title_wrong_format():
    netlink_factory = aEntriesLink().with_S1A_form_name().without_CIK()
    netlink = netlink_factory.get()
    entire_doc = netlink.get(None, None)
    entire_entries = netlink._break_to_entities(entire_doc)
    assert len(entire_entries) == 1
    entire_entry = entire_entries[0]
    with pytest.raises(BaseException):
        netlink.parse_form_title(entire_entry)


class aEntriesLink:
    def __init__(self):
        self.entire_doc_template = """<entry>
            {title}
            <link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/1844417/000110465921080274/0001104659-21-080274-index.htm"/>
            {summary}
            <updated>2021-06-11T17:19:36-04:00</updated>
            <category scheme="https://www.sec.gov/" label="form type" term="S-1/A"/>
            <id>urn:tag:sec.gov,2008:accession-number=0001104659-21-080274</id>
            </entry>
            """
        self.title_template = (
            "<title>{form_name} - {company_name} {CIK_in_parens} (Filer)</title>"
        )
        self.form_name = "S-1"
        self.company_name = "TradeUP Acquisition Corp."
        self.CIK_in_parens = "(0001844417)"
        self.summary_template = """
             <summary type="html">
            {summary_content} &lt;b&gt;AccNo:&lt;/b&gt; 0001104659-21-080274 &lt;b&gt;Size:&lt;/b&gt; 2 MB
            </summary>
        """
        self.summary_content_template = "&lt;b&gt;{filed}&lt;/b&gt; {date}"
        self.filed = "Filed:"
        self.date = "2021-06-11"

    @property
    def datetime(self):
        if self.date:
            return datetime.strptime(self.date, r"%Y-%m-%d")
        else:
            return None

    def with_S1A_form_name(self):
        self.form_name = "S-1/A"
        return self

    def without_CIK(self):
        self.title_template = "<title>{form_name} - {company_name} </title>"
        return self

    def without_date(self):
        self.date = ""
        return self

    def without_filed(self):
        self.filed = ""
        return self

    def with_two_summary_tags_one_date(self):
        self.summary_content_template = (
            self.summary_content_template
            + self.summary_content_template.format(date="", filed="{filed}")
        )
        return self

    def without_summary(self):
        self.summary_template = ""
        return self

    def with_2_different_filed(self):
        self.summary_content_template = (
            self.summary_content_template + " &lt;b&gt;{filed}&lt;/b&gt; 2020-01-01"
        )
        return self

    def with_2_identical_filed(self):
        self.summary_content_template = (
            self.summary_content_template + " " + self.summary_content_template
        )
        return self

    def get(self):
        title = self.title_template.format(
            form_name=self.form_name,
            company_name=self.company_name,
            CIK_in_parens=self.CIK_in_parens,
        )
        summary_content = self.summary_content_template.format(
            date=self.date, filed=self.filed
        )
        summary = self.summary_template.format(summary_content=summary_content)
        return MockEntriesLink(
            self.entire_doc_template.format(title=title, summary=summary)
        )
