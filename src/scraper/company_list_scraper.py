from datetime import datetime
from time import sleep
import tqdm
import pandas as pd
from csv import QUOTE_ALL
from offline.infra.netlink import NetLink
import re
from parse import search


class EntriesLink(NetLink):
    entity_name = "entry"

    def parse_entity(self, ent):
        res = {}
        # if these fail, we don't have a valid entry
        try:
            form_title = self.parse_form_title(ent)
            res.update(form_title)
            res.update({"link": self._entity_component_attr(ent, "link", "href")})
        except BaseException:
            return {}

        try:
            res.update(self._extract_issued_date(ent))
        except BaseException:
            pass
        return res

    def parse_form_title(self, ent):
        form_title_full_text = self._entity_component_text(ent, "title")
        form_title = search(
            "{form_type} - {company_name} ({CIK})", form_title_full_text
        )
        if not form_title:
            raise Exception("malformed entry")

        return form_title.named

    def entity_filter(self, ent):
        return ent["form_type"].lower() == "s-1"

    def _extract_issued_date(self, ent):
        list_text_containing_issued_date = self._entity_component_interior_html(
            ent, "summary"
        )
        issued_str = set()
        for candidate in list_text_containing_issued_date:
            issued_str |= set(
                re.findall(
                    "Filed[^0-9]+([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])",
                    candidate,
                )
            )
        if len(issued_str) != 1:
            issued_dict = {}
        else:
            issued_datetime = datetime.strptime(issued_str.pop(), r"%Y-%m-%d")
            issued_dict = {"date_issued": issued_datetime}
        return issued_dict


def multi_page_query(url, params):
    net_link = EntriesLink()
    all_recent_entries = []
    for start in tqdm.tqdm(range(0, MAX_ENTRIES, EDGAR_ENTRIES_PER_PAGE)):
        params.update({"start": start})
        try:
            all_recent_entries += one_page_query(net_link, url, params)
        except BaseException as e:
            print(e)
            break
    return all_recent_entries


def one_page_query(net_link, url, params):
    entire_document = net_link.get(url, params, retries=10)
    return net_link.parse_entities(entire_document)


if __name__ == "__main__":
    form_type = "S-1"
    MAX_ENTRIES = 1000
    EDGAR_ENTRIES_PER_PAGE = 100
    edgar_url = r"https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "company": "",
        "CIK": "",
        "type": form_type,
        "owner": "include",
        "count": 100,
        "action": "getcurrent",
        "dateb": "",
        "output": "atom",
    }

    all_recent_entries = multi_page_query(edgar_url, params)
    links_file = "Going_public.csv"  # f"links_{datetime.now().strftime(r'%Y%m%d')}.csv"
    pd.DataFrame(all_recent_entries).to_csv(links_file, index=False, quoting=QUOTE_ALL)
