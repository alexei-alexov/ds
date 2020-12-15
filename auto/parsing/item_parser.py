from operator import itemgetter

from pprint import pprint
import json

from bs4 import BeautifulSoup
from parsing.utils import get_item_page


def prepare_selector(query, t=str):
    keys = query.split('.')
    def _selector(data):
        for key in keys:
            data = data.get(key)
            if not data: break

        if data: data = t(data)
        return data
    return _selector


class ItemParser:

    base_url = 'https://auto.ru/cars/used/sale/'

    mapping = {
        'bodyType': prepare_selector('state.card.vehicle_info.configuration.human_name'),
        'color': prepare_selector('meta.color'),
        'fuelType': prepare_selector('meta.fuelType'),
        'modelDate': prepare_selector('meta.modelDate', int),
        'productionDate': prepare_selector('meta.productionDate', int),
        'numberOfDoors': prepare_selector('meta.numberOfDoors', int),
        'brand': prepare_selector('meta.brand'),
        'name': prepare_selector('state.card.vehicle_info.tech_param.human_name'),
        'vehicleConfiguration': prepare_selector('meta.vehicleConfiguration'),
        'vehicleTransmission': prepare_selector('meta.vehicleTransmission'),
        'engineDisplacement': prepare_selector('meta.vehicleEngine.engineDisplacement'),
        'enginePower': prepare_selector('meta.vehicleEngine.enginePower'),
        'description': prepare_selector('meta.description'),
        'mileage': prepare_selector('state.card.state.mileage', int),
        'Комплектация': prepare_selector('state.card.vehicle_info.equipmentGroups'),
        'Привод': prepare_selector('card.CardInfoRow_drive'),
        'Руль': prepare_selector('card.CardInfoRow_wheel'),
        'Состояние': prepare_selector('card.CardInfoRow_state'),
        'Владельцы': prepare_selector('card.CardInfoRow_ownersCount'),
        'ПТС': prepare_selector('card.CardInfoRow_pts'),
        'Таможня': prepare_selector('card.CardInfoRow_customs'),
        'Владение': prepare_selector('card.CardInfoRow_owningTime'),
        'Price': prepare_selector('state.card.price_info.price')
    }

    def __init__(self, use_proxy=True):
        self.use_proxy = use_proxy

    def parse_page(self, id):
        r = get_item_page(id, use_proxy=self.use_proxy)
        r.encoding = 'utf8'
        s = BeautifulSoup(r.text, 'html.parser')
        try:
            initial_state = json.loads(s.find('script', id='initial-state').contents[0])
            card_info = {}
            for li in s.find('ul', class_='CardInfo').contents:
                card_info[li['class'][-1]] = list(li.children)[-1].text.replace('\xa0', ' ')
            meta = {}
            for meta_item in s.find('span', itemtype='http://schema.org/Car').contents:
                if meta_item.name == 'span':
                    s = {}
                    for sub_item in meta_item.children:
                        s[sub_item['itemprop']] = sub_item['content']
                    meta[meta_item['itemprop']] = s
                else:
                    meta[meta_item['itemprop']] = meta_item['content']
            # aggregate all the data into a single dict
            database = {
                'state': initial_state,
                'card': card_info,
                'meta': meta,
            }
            # prepare fields
            result = {}
            for key, selector in self.mapping.items():
                result[key] = selector(database)

            return result
        except Exception as error:
            print("Parse card error: %s, id: %s" % (error, id,))
            raise


if __name__ == '__main__':
    parser = ItemParser()
    r = parser.parse_page('1101560077-abbfee6a')
    # print(r)

