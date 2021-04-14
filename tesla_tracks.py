from argparse import ArgumentParser
from CONSTS import C
import requests
from teslapy import Tesla


def main():
    print(C.USERNAME)


if __name__ == '__main__':
    parser = ArgumentParser(description='Poll data from the Tesla API and store it in ElasticSearch')
    args = parser.parse_args()

    main()
