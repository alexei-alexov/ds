import requests
import time
import random


proxy = {
    'http': 'socks5h://localhost:5555',
    'https': 'socks5h://localhost:5555',
}
list_base_url = 'https://auto.ru/moskva/cars/all/'
item_base_url = 'https://auto.ru/cars/used/sale/{car_id}'


def _get_request(link: str, use_proxy=True, **extra):
    """Base request function"""
    if use_proxy:
        extra['proxies'] = proxy

    time.sleep(random.random() * 0.5)
    r = requests.get(link, **extra)
    r.raise_for_status()
    return r


def get_list_page(page_no: int, **extra):
    """Return list of cars on given page"""
    return _get_request(
        list_base_url,
        params={'page': page_no, 'output_type': 'list'},
        **extra
    )


def get_item_page(car_id: str, **extra):
    """Return car page content"""
    return _get_request(item_base_url.format(car_id=car_id), **extra)
