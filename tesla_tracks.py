from argparse import ArgumentParser
from CONSTS import C
from datetime import datetime
import json
import requests
from statistics import mean
from teslapy import Tesla
from time import sleep, strftime, gmtime, mktime


def authorize():
    tesla_api = Tesla(C.USERNAME, C.PASSWORD)
    tesla_api.headers['User-Agent'] = 'ProjectWardenclyffe - adrong@gmail.com; TeslaPy; ' + tesla_api.headers['User-Agent']
    tesla_api.fetch_token()
    return tesla_api


def fixup_epoch_timestamp(json_obj, timestamp_formatting='%Y-%m-%dT%H:%M:%SZ', timestamp_field='timestamp', fixed_timestamp_field='@timestamp', milliseconds=True):
    if timestamp_field in json_obj:
        print('formatting timestamp for ES')
        json_obj[fixed_timestamp_field] = strftime(timestamp_formatting, gmtime(json_obj[timestamp_field]/(1000 if milliseconds else 1)))
    return json_obj


def main():
    tesla_api = authorize()
    sleep_interval = 1

    while True:
        sleep(sleep_interval)
        sleep_interval = 1  # Reset the sleep interval if it had been set to something else in the loop
        vehicles = tesla_api.vehicle_list()
        print(vehicles[0]['display_name'])
        if vehicles[0]['state'] == 'online':
            print('is online')
            if vehicles[0]['in_service']:
                print('is in service')
            else:
                # User probably woke the car up from the phone meaning we can likely capture data,  but we don't want to
                # keep the car awake by accident. Wait 15min so car has chance to fall back asleep.
                # In most (if not all) cases, this is likely redundant with the `is_user_present` condition below.
                print('Car is not in service. Will wait 15min.')
                sleep_interval = 15*60+1

            try:
                vd = vehicles[0].get_vehicle_data()
                print('got data')
            except Exception as e:
                print('!!!!!!!!!EXCEPTION RAISED:', e)
                print('VEHICLES:', vehicles)
                sleep(1)
                continue

            _id = vehicles[0]['vin'][12:] + str(int(mktime(gmtime())))  # TODO: grab VIN from the vehicle data `vd` instead.
            print('generated GUID')
            timestamps = []
            for k,v in vd.items():
                if isinstance(v, dict):
                    if 'timestamp' in v:
                        timestamps.append(v['timestamp'])
            vd['timestamp'] = mean(timestamps)

            fixup_epoch_timestamp(vd)  # `vd` is updated via pass-by-ref.
            r = requests.put('http://elasticsearch.deep13.lol:9200/{index}/_doc/{id}'.format(index='test_la', id=_id),
                             headers={'content-type': 'application/json'}, data=json.dumps(vd))
            print(r.status_code, r.text)

            if not vd['vehicle_state']['is_user_present']:
                print('No driver present. Waiting 15min')
                sleep_interval = 15*60+1  # No one is in the car, wait 15min so the car has a chance to go to sleep.

        elif not vehicles[0]['in_service']:
            print('Not in service. Waiting 15min')
            sleep_interval = 15*60+1  # Car is asleep or wants to be. Wait 15min before retry


if __name__ == '__main__':
    parser = ArgumentParser(description='Poll data from the Tesla API and store it in ElasticSearch')
    args = parser.parse_args()

    main()
