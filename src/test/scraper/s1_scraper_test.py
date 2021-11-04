import numpy as np
import pandas as pd
import math
from offline.scraper.s1_scraper import TableLink, CrossBuilder

# TODO
# - [x] Find all tables
# - [x] filter the (candidate) right one by keywords
# - [x] remove lines/cols with all nulls (but not partial)
# - [ ] find crosses :
#               |
#               |
#              2020 <--- year
#               |
#               |
# revenue --- 1234 ---- <---(revenue=regex)
#               |
#               |
#               |
# and save them like so Cross(row_indicator,col_indicator,value)
# - [ ] find crosses with same keyword, but different year, and merge to a dataframe
# - [ ] return a list of dataframes, each based on a set of crosses


def test_remove_col_all_nulls():
    df = pd.DataFrame({"a": [None, None], "b": [3, 4]})
    res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_col_all_nulls)
    assert res.shape == (2, 1)
    assert "b" in res.columns
    assert "a" not in res.columns
    assert res.b.to_list() == [3, 4]


def test_remove_col_all_nulls_nothing_to_remove():
    df = pd.DataFrame({"a": [None, 5], "b": [3, 4]})
    res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_col_all_nulls)
    assert df.equals(res)


def test_remove_row_all_nulls():
    df = pd.DataFrame({"a": [1, None], "b": [3, None]})
    res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_row_all_nulls)
    assert res.shape == (1, 2)
    assert "b" in res.columns
    assert "a" in res.columns
    assert np.all(res.to_numpy() == np.array([[1, 3]]))


def test_remove_row_all_nulls():
    df = pd.DataFrame({"a": [1, None], "b": [3, None]})
    res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_row_all_nulls)
    assert res.shape == (1, 2)
    assert "b" in res.columns
    assert "a" in res.columns
    assert np.all(res.to_numpy() == np.array([[1, 3]]))


def test_remove_row_all_nulls_nothing_to_remove():
    df = pd.DataFrame({"a": [None, 5], "b": [3, 4]})
    res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_row_all_nulls)
    assert df.equals(res)


def test_crossify():
    df = pd.DataFrame(  # fmt: off
        np.array(
            [  # fmt: off
                [None, 2020, 3],  # fmt: off
                ["revenue coco", 13.0, "oh"],  # fmt: off
                ["blah", 33, 54],  # fmt: off
            ]
        )  # fmt: off
    )  # fmt: off
    cross_builder = CrossBuilder("[rR]evenue", [2019, 2020],2020)
    cross_list = cross_builder(df)
    assert len(cross_list) == 1
    cross = cross_list[0]
    assert cross.row_indicator == "revenue coco"
    assert cross.col_indicator == 2020
    assert math.isclose(cross.value, 13.0, abs_tol=1e-7)
    # assert cross.row_indicator =
    # res = df.pipe(TableLink._start_pipeline).pipe(TableLink._remove_row_all_nulls)
    # assert df.equals(res)
