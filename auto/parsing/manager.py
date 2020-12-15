# AAAAA
from parsing.item_parser import ItemParser
from parsing.list_parser import ListParser
import csv
import threading
import time




class Manager:

    """Manage data provided by parsers and to parsers"""

    order = [
        'bodyType', 'brand', 'color', 'fuelType', 'modelDate', 'name', 'numberOfDoors', 'productionDate',
        'vehicleConfiguration', 'vehicleTransmission', 'engineDisplacement', 'enginePower', 'description',
        'mileage', 'Комплектация', 'Привод', 'Руль', 'Состояние', 'Владельцы', 'ПТС', 'Таможня', 'Владение', 'id',
        'Price'
    ]

    def __init__(self):
        pass

    def load(self):
        # 600
        list_parser = ListParser(pages=(600, 5000))
        item_parser = ItemParser()
        finished = False
        parsed_data = []
        ids_to_parse = []
        def save_data():
            _id = 1
            with open('data.csv', 'a', newline='', encoding='utf-8') as csv_f:
                writer = csv.writer(csv_f, delimiter=',', quotechar='"')
                while not finished or parsed_data:
                    try:
                        item = parsed_data.pop()
                        item['id'] = _id
                        _id += 1
                        writer.writerow([item.get(key) for key in self.order])
                        csv_f.flush()
                        if _id % 20 == 0:
                            print("Saved %d records" % (_id,))
                    except IndexError:
                        time.sleep(0.5)
                        continue
            print("Saved %d records" % (_id,))

        save_thread = threading.Thread(target=save_data)
        save_thread.start()

        def parse_list():
            nonlocal finished
            generator = list_parser.parse()
            while True:
                if len(ids_to_parse) >= 1000:
                    time.sleep(1)
                    continue
                try:
                    car_id = next(generator)
                    ids_to_parse.append(car_id)
                except Exception as error:
                    print(error)
            finished = True

        list_parser_thread = threading.Thread(target=parse_list)
        list_parser_thread.start()

        def parse_car():
            while not finished or ids_to_parse:
                try:
                    car_id = ids_to_parse.pop()
                except IndexError:
                    time.sleep(0.5)
                    continue
                try:
                    parsed_data.append(item_parser.parse_page(car_id))
                except Exception as error:
                    print('Cannot parse car page: %s' % (error,))

        car_parsers = [threading.Thread(target=parse_car) for _ in range(3)]
        for car_parser in car_parsers: car_parser.start()
        for car_parser in car_parsers: car_parser.join()
        finished = True
        save_thread.join()
        print("DONE")




if __name__ == '__main__':
    m = Manager()
    m.load()
