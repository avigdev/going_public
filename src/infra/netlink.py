import gazpacho
from time import sleep
import random


class NetLink:
    SLEEP = 1

    def get(self, url, params, retries=3):
        try:
            sleep(self.SLEEP * (1.0 + random.random()))
            entire_document = gazpacho.get(url, params)
            return entire_document
        except BaseException as e:  # noqa
            if retries > 0:
                return self.get(url, params, retries - 1)
            return ""

    def entity_filter(self, ent):
        return True

    def entity_transform(self, ent):
        return ent

    def parse_entities(self, entire_document):
        cur_entities = self._break_to_entities(entire_document)
        cur_parsed_entries = [self.parse_entity(ent) for ent in cur_entities if ent]
        cur_parsed_entries = filter(self.entity_filter, cur_parsed_entries)
        cur_parsed_entries = list(map(self.entity_transform, cur_parsed_entries))
        return cur_parsed_entries

    def _break_to_entities(self, entire_document):
        soup = gazpacho.Soup(entire_document)
        cur_entities = soup.find(self.entity_name, mode="all")
        return cur_entities

    @staticmethod
    def _entity_component_text(ent, component):
        return ent.find(component).text

    @staticmethod
    def _entity_component_attr(ent, component, attr):
        return ent.find(component).attrs[attr]

    @staticmethod
    def _entity_component_interior_html(ent, component):
        res = ent.find(component, mode="all")
        res_list = [x.html for x in res]
        return res_list

    @staticmethod
    def _entity_component_text_all(ent, component):
        res = ent.find(component, mode="all")
        res_list = [x.text for x in res]
        return res_list

    def parse_entity(self, ent):
        raise NotImplementedError("derived class should implement parse_entity")
