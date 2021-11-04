import tqdm
from offline.infra.netlink import NetLink
import pandas as pd
import numpy as np
from csv import QUOTE_ALL
from dataclasses import dataclass
from collections import namedtuple,defaultdict
from itertools import chain, combinations
from datetime import datetime
import functools

# Cross = namedtuple("Cross", "row_indicator col_indicator value is_quarterly")
Cross = namedtuple("Cross", "row_indicator col_indicator value")
# @dataclass
# class Cross:
#     """
#     crosses are parts of tables that include a central cell,
#     and two cells from the same column/row
#     that serve to identify the meaning of the central cell. For example:

#                     |
#                     |
#                     2020 <--- year
#                     |
#                     |
#     ---- revenue -- 1234.5 ----
#                     |
#                     |
#                     |
#     in this example, the row indicator is "revenue", the col indicator is 2020,
#     and the cell value is 1234.5
#     """

#     row_indicator: str
#     col_indicator: str
#     value: float
#     is_quarterly : bool


class CrossBuilder:
    def __init__(
        self, row_keyword_regex, col_value_list, max_col_value, only_floats=True
    ):
        self.row_keyword_regex = row_keyword_regex
        self.col_value_list = [v for v in col_value_list if v <= max_col_value]
        self.only_floats = only_floats

    def _extract_row_indicator_places(self, df):
        nrow = df.shape[0]
        is_pattern_matched = [
            df.iloc[x, :].str.contains(self.row_keyword_regex, case=False)
            for x in range(nrow)
        ]
        row_inds, col_inds = np.nonzero(is_pattern_matched)
        return row_inds, col_inds

    def _extract_col_indicator_places(self, df):
        ncols = df.shape[1]
        is_col_header_found = [
            np.any(
                [df.iloc[:, x].astype(str) == str(y) for y in self.col_value_list],
                axis=0,
            )
            for x in range(ncols)
        ]
        col_inds, row_inds = np.nonzero(
            is_col_header_found
        )  # note that we iterated over columns
        return row_inds, col_inds

    def __call__(self, df):
        df_str = df.applymap(lambda x: str(x or ""))  # convert None to ""
        row_indicator_places = self._extract_row_indicator_places(df_str)
        col_indicator_places = self._extract_col_indicator_places(df_str)
        crosses = []
        for row_ind_i, row_ind_j in zip(*row_indicator_places):
            for col_ind_i, col_ind_j in zip(*col_indicator_places):
                number_found_is_the_indicator = row_ind_i <= col_ind_i
                if number_found_is_the_indicator:
                    continue
                try:
                    assert np.isfinite(float(df.iloc[row_ind_i, col_ind_j]))
                except BaseException:
                    if self.only_floats:
                        continue
                if self.only_floats:
                    crosses.append(
                        Cross(
                            df.iloc[row_ind_i, row_ind_j],
                            df.iloc[col_ind_i, col_ind_j],
                            float(df.iloc[row_ind_i, col_ind_j]),
                        )
                    )
                else:
                    crosses.append(
                        Cross(
                            df.iloc[row_ind_i, row_ind_j],
                            df.iloc[col_ind_i, col_ind_j],
                            df.iloc[row_ind_i, col_ind_j],
                        )
                    )
        return list(sorted(set(crosses), key=lambda x: x[1:]))


class TableLink(NetLink):
    entity_name = "table"

    def _break_to_entities(self, entire_document):
        all_tables = pd.read_html(entire_document)
        return all_tables

    def parse_entity(self, ent):
        return ent

    def _keyword_filter(self,keyword,df):
        res = df.applymap(lambda x: keyword in str(x).lower()).any(
            axis=None
        )
        return res

    def entity_filter(self, ent,keywords = ["revenue","consolidated","thousadns"] ):
        not_masked = {k:self._keyword_filter(k,ent) for k in keywords}
        # compulsary_key = keywords[0]
        # keys_powerset = chain.from_iterable(combinations(keywords[1:],r) for r in range(len(keywords)+1))
        # res = defaultdict(lambda:True)
        # for keys in keys_powerset:
        #     keys_with_compulsary = (compulsary_key,) + keys
        #     for k in keys_with_compulsary:
        #         res[keys] &= not_masked[k]
        res = True
        for k in keywords:
            res &= not_masked[k] 
        return res

    def post_process(self,crosses_list):
        """
        create quarterly and yearly per year by the following logic:
        per title + year - larger values are yearly and smaller quarterly
        if there is more than one title - take the shorter one (?)

        output should be two dataframes - yearly and quarterly (if exists)
        cik, revenue, year

        these can afterwards be joined and maximized over year, if needed
        """
        # collect titles - and filter only the shorter
        # 
        return crosses_list

    def parse_entities(self, entire_document):
        cur_parsed_entries = self._break_to_entities(entire_document)
        partial_filter = functools.partial(self.entity_filter,keywords=["revenue"])
        cur_parsed_entries = list(filter(partial_filter, cur_parsed_entries))
        cur_parsed_entries = list(map(self.entity_transform, cur_parsed_entries))
        # deduping is fine - but separate between quarterly and yearly
        deduped = sorted({entry for per_table_entries in cur_parsed_entries for entry in per_table_entries},key=lambda x: x[1:])
        return deduped

    @staticmethod
    def _start_pipeline(df):
        return df.copy()

    @staticmethod
    def _remove_col_all_nulls(df):
        df.dropna(axis=1, how="all", inplace=True)
        return df

    @staticmethod
    def _remove_row_all_nulls(df):
        df.dropna(axis=0, how="all", inplace=True)
        return df

    def entity_transform(self, ent):
        cur_year = datetime.today().year
        cross_builder = CrossBuilder(
            "^(?:[ ]*revenue[sS]*[., ]*|[ ]*total.+revenue[sS][ ]*)",
            list(range(2015, 2100)),
            cur_year,
        )
        return cross_builder(ent)
        # ent.dropna(axis=0,how='all',inplace = True)
        # ent.dropna(axis=1,how='all',inplace = True)
        # ent = ent.iloc[ent.iloc[:,0].str.contains('revenue',case=False).fillna(True).to_numpy(),:]
        # ent = ent.iloc[:,[ent.iloc[:,x].str.contains('year|revenue',case=False).fillna(False).any() for x in range(ent.shape[1])]]
        # relevant_years = range(2015,2100)
        # row_indices = np.flatnonzero([ent.iloc[x,:].str.contains('revenue',case=False).fillna(False).any() for x in range(ent.shape[0])])
        # col_indices1 = np.flatnonzero([ent.iloc[:,x].str.contains('year',case=False).fillna(False).any() for x in range(ent.shape[1])])
        # col_indices2 = np.flatnonzero([np.any([ent.iloc[:,x].str.contains(str(y)).fillna(False) for y in relevant_years]) for x in range(ent.shape[1])])
        # col_indices = np.array(list(set(col_indices1) & set(col_indices2)))
        # year_rows = np.array([y1 for y1 in [[ent.iloc[:,x].str.contains(str(y)).apply(lambda x: x if x else np.nan).first_valid_index() for x in range(ent.shape[1])] for y in relevant_years] if np.any(y1)]).flatten()
        # year_rows = np.array(list({x for x in year_rows if x is not None}))
        # # ent = ent.iloc[ent.iloc[0].str.contains('revenue',case=False).fillna(True).to_numpy(),:]
        # return [ent.iloc[row_indices,col_indices]]


def obtain_links(file_stream, company_id_col="CIK", link_col="s1_link"):
    df = pd.read_csv(file_stream, dtype=str)
    df = df.set_index(company_id_col)
    return df.to_dict()[link_col]


if __name__ == "__main__":
    csvfile = r"/home/avi/code/s1/online/s1_forms.csv"
    with open(csvfile, "rt") as f:
        links_per_cik = obtain_links(f)

    net_link = TableLink()
    res = []
    i = 0
    for cik, url in tqdm.tqdm(links_per_cik.items()):
        try:
            # url = "https://www.sec.gov" + url
            entire_document = net_link.get(url, "", retries=10)
            all_docs = net_link.parse_entities(entire_document)
            res.append({"CIK": cik, "blob": all_docs})
        except BaseException as e:
            print(f"got exception {e}")

    pd.DataFrame(res).to_csv("s1_fields.csv", index=False, quoting=QUOTE_ALL)

    # # url = "https://www.sec.gov/Archives/edgar/data/1861104/000119312521206391/d108549ds1.htm"
    # # url = "https://www.sec.gov/Archives/edgar/data/1672688/000162828021013214/abscis-1.htm"
    # url = "https://www.sec.gov/Archives/edgar/data/1783879/000162828021013318/robinhoods-1.htm"

    # net_link = TableLink()
    # try:
    #     entire_document = net_link.get(url, "", retries=10)
    #     x = net_link.parse_entities(entire_document)
    #     print(len(x))
    #     print(x)
    # except BaseException as e:
    #     print(e)
