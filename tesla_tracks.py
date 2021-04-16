from argparse import ArgumentParser
from CONSTS import C
from datetime import datetime
import json
import requests
from teslapy import Tesla
from time import sleep, strftime, gmtime, mktime


def authorize():
    tesla_api = Tesla(C.USERNAME, C.PASSWORD)
    tesla_api.headers['User-Agent'] = 'ProjectWardenclyffe - adrong@gmail.com; TeslaPy; ' + tesla_api.headers['User-Agent']
    tesla_api.fetch_token()
    return tesla_api


def fixup_epoch_timestamp(json_obj, timestamp_formatting='%Y-%m-%dT%H:%M:%SZ', timestamp_field='timestamp', fixed_timestamp_field='@timestamp', milliseconds=True):
    if timestamp_field in json_obj:
        json_obj[fixed_timestamp_field] = strftime(timestamp_formatting, gmtime(json_obj[timestamp_field]/(1000 if milliseconds else 1)))
    return json_obj


def main():
    tesla_api = authorize()

    while True:
        vehicles = tesla_api.vehicle_list()
        print(vehicles[0]['display_name'])
        if vehicles[0]['state'] == 'online':
            vd = vehicles[0].get_vehicle_data()
            # 'vin': '5YJ3E1EA2MF871477'
            _id = vehicles[0]['vin'][12:] + str(int(mktime(gmtime())))  # TODO: grab VIN from the vehicle data `vd` instead.
            for k,v in vd.items():
                if isinstance(v, dict):
                    vd[k] = fixup_epoch_timestamp(v)

                    r = requests.put('http://elasticsearch.deep13.lol:9200/{index}/_doc/{id}'.format(index='test_'+k, id=_id),
                                     headers={'content-type': 'application/json'}, data=json.dumps(v))
                    print(r.status_code, r.text)
                    print('\n')
        sleep(15)


if __name__ == '__main__':
    parser = ArgumentParser(description='Poll data from the Tesla API and store it in ElasticSearch')
    args = parser.parse_args()

    main()
