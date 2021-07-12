import json
import requests
from CONSTS import C
from teslapy import Tesla
from statistics import mean
from threading import Thread
from argparse import ArgumentParser
from datetime import timedelta, datetime
from time import sleep, strftime, gmtime, mktime


def authorize():
    print('Logging in as', C.USERNAME)
    tesla_api = Tesla(C.USERNAME, C.PASSWORD)
    tesla_api.headers['User-Agent'] = 'ProjectWardenclyffe - adrong@gmail.com; TeslaPy; ' + tesla_api.headers['User-Agent']
    tesla_api.fetch_token()
    return tesla_api


def fixup_epoch_timestamp(json_obj, timestamp_formatting='%Y-%m-%dT%H:%M:%SZ', timestamp_field='timestamp', fixed_timestamp_field='@timestamp', milliseconds=True):
    if timestamp_field in json_obj:
        print('formatting timestamp for ES')
        json_obj[fixed_timestamp_field] = strftime(timestamp_formatting, gmtime(json_obj[timestamp_field]/(1000 if milliseconds else 1)))
    return json_obj


def _get_vehicle_info(vehicle):
    sleep_interval = 1
    print(vehicle['display_name'])
    if vehicle['state'] == 'online':
        vd = {}
        print('is online')
        try:
            vd = vehicle.get_vehicle_data()
            print('got data')
        except Exception as e:
            print('!!!!!!!!!EXCEPTION RAISED:', e)
            print('VEHICLE:', vehicle)
            sleep(1)

        _id = vehicle['vin'][12:] + str(int(mktime(gmtime())))  # TODO: grab VIN from the vehicle data `vd` instead.
        print('generated GUID')
        timestamps = []
        for k, v in vd.items():
            if isinstance(v, dict):
                if 'timestamp' in v:
                    timestamps.append(v['timestamp'])
        vd['timestamp'] = mean(timestamps)

        fixup_epoch_timestamp(vd)  # `vd` is updated via pass-by-ref.
        r = requests.put('http://elasticsearch.deep13.lol:9200/{index}/_doc/{id}'.format(index='test_la', id=_id),
                         headers={'content-type': 'application/json'}, data=json.dumps(vd))
        print(r.status_code, r.text)

        if not vd['vehicle_state']['is_user_present']:
            if vd['climate_state']['is_climate_on']:
                print('Climate is on. Expecting driver soon.')
                sleep_interval = 1
            else:
                print('No driver present. Waiting 15min')
                sleep_interval = 15 * 60 + 1  # No one is in the car, wait 15min so the car has a chance to go to sleep.
    elif not vehicle['in_service']:
        print('Not in service. Waiting 10sec')
        sleep_interval = 10  # Car is asleep. Retry, but not too fast.
    sleep(sleep_interval)


def main():
    thirty_minutes = timedelta(minutes=30)

    tesla_api = authorize()
    vehicles = []

    last_vehicle_refresh = datetime(1970, 1, 1)
    vehicle_threads = {}

    while True:
        if datetime.now() - last_vehicle_refresh > thirty_minutes:
            print('refreshed vehicle list')
            last_vehicle_refresh = datetime.now()
            vehicles = tesla_api.vehicle_list()

        for vehicle in vehicles:
            if (vehicle['vin'] not in vehicle_threads) or (not vehicle_threads[vehicle['vin']].is_alive()):
                vehicle_threads[vehicle['vin']] = Thread(target=_get_vehicle_info, args=(vehicle,))
                vehicle_threads[vehicle['vin']].start()

        # break


if __name__ == '__main__':
    parser = ArgumentParser(description='Poll data from the Tesla API and store it in ElasticSearch')
    args = parser.parse_args()

    main()
