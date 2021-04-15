from argparse import ArgumentParser
from CONSTS import C
from datetime import datetime
import json
import requests
from teslapy import Tesla
from time import sleep, strftime, gmtime

def authorize():
    tesla_api = Tesla(C.USERNAME, C.PASSWORD)
    tesla_api.fetch_token()
    return tesla_api


def fixup_epoch_timestamp(json_obj, timestamp_formatting='%Y/%m/%d %H:%M:%SZ', timestamp_field='timestamp', fixed_timestamp_field='@timestamp', milliseconds=True):
    if timestamp_field in json_obj:
        json_obj[fixed_timestamp_field] = strftime(timestamp_formatting, gmtime(json_obj[timestamp_field]/(1000 if milliseconds else 1)))
    return json_obj


def main():
    tesla_api = authorize()
    vehicles = tesla_api.vehicle_list()
    # if vehicles[0][C.TESLA_API_VEHICLE_KEYWORD_STATE] == C.TESLA_API_VEHICLE_STATE_VALUE_ONLINE:
    #     vd = vehicles[0].get_vehicle_data()
    #
    #     # 182569493226
    #
    #     r = requests.put('http://elasticsearch.deep13.lol:9200/tesla_test/vehicles/1', headers={'content-type': 'application/json'}, data=json.dumps(vd))
    #     print(r.status_code)
    #     print(r.text)
    #     sleep(30)
    vd = vehicles[0].get_vehicle_data()
    for k,v in vd.items():
        if isinstance(v, dict):
            vd[k] = fixup_epoch_timestamp(v)

            r = requests.put('http://elasticsearch.deep13.lol:9200/{index}/{type}/{id}'.format(index='test_'+k, type=vd['vin'][3:4], id=2), headers={'content-type': 'application/json'}, data=json.dumps(vd))
            print(r.status_code, r.text)
            print('')


if __name__ == '__main__':
    parser = ArgumentParser(description='Poll data from the Tesla API and store it in ElasticSearch')
    args = parser.parse_args()

    main()
