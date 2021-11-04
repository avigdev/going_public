import io
from offline.scraper.form_materials_scraper import obtain_links


def test_obtain_links():
    stream = io.StringIO(
        """
    "form_type","company_name","CIK","link","date_issued"
    "S-1","Katapult Holdings, Inc.","0001785424","/y1.htm","2021-06-30"
    "S-1","Desktop Metal, Inc.","0001754820","/y2.htm","2021-06-30"
    """
    )
    links = obtain_links(stream, company_id_col="CIK", link_col="link")
    assert links["0001785424"] == "/y1.htm"
    assert links["0001754820"] == "/y2.htm"
