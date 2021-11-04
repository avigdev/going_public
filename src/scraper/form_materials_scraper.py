import tqdm
from offline.infra.netlink import NetLink
import pandas as pd
from csv import QUOTE_ALL


class TrLink(NetLink):
    SLEEP = 5
    entity_name = "tr"

    def parse_entity(self, ent):
        res = {}
        # if these fail, we don't have a valid entry
        try:
            res = {
                "link": r"https://www.sec.gov"
                + self._entity_component_attr(ent, "a", "href")
            }
            res.update({"doc_type": self._entity_component_text_all(ent, "td")[3]})
            return res
        except BaseException:
            return {}

    def entity_filter(self, ent):
        return "doc_type" in ent and ent["doc_type"].lower() == "s-1"


def obtain_links(file_stream, company_id_col="CIK", link_col="link"):
    df = pd.read_csv(file_stream, usecols=[company_id_col, link_col], dtype=str)
    df = df.set_index(company_id_col)
    return df.to_dict()[link_col]


if __name__ == "__main__":
    csvfile = "Going_public.csv"
    net_link = TrLink()
    with open(csvfile, "rt") as f:
        links_per_cik = obtain_links(f)

    res = []
    for cik, url in tqdm.tqdm(links_per_cik.items()):
        entire_document = net_link.get(url, "", retries=10)
        all_docs = net_link.parse_entities(entire_document)
        if len(all_docs) == 1:
            res.append({"CIK": cik, "s1_link": all_docs[0]["link"]})

    pd.DataFrame(res).to_csv("s1_forms.csv", index=False, quoting=QUOTE_ALL)
