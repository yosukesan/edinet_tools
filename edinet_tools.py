#!/usr/bin/env python3

import os, json, logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from edinet import EdinetTool

def yaxbrl_read_cache_data(file_path):

    if not os.path.isfile(file_path):
        logging.error('@{0}: Error number = {1}\n\t{2}' \
            .format(yaxbrl_get.__name__, 0, edinet.error_code[0]))
        sys.exit(1)

    rfile = open(edinet.cache_file_path, 'r')
    cache_data = json.load(rfile)
    rfile.close()

    return cache_data

def yaxbrl_update(edinet, tart, end):

    new_data = edinet.metadata_get(start, end)
    previous_data = None

    if not os.path.isdir(edinet.cache_dir_path):
        print('making local cache dir : ', edinet.cache_dir_path)
        os.makedirs(edinet.cache_dir_path)
    else:
        if os.path.isfile(edinet.cache_file_path):
            print('reading local cache file : ', edinet.cache_file_path)
            rfile = open(edinet.cache_file_path, 'r')
            previous_data = json.load(rfile)
            rfile.close()
            new_data = dict(new_data) | previous_data

    wfile = open(edinet.cache_file_path, 'w')
    print('Downloading meta json file')
    json.dump(new_data, wfile)
    wfile.close()

def yaxbrl_get(edinet, start, end, is_exclude_fund):

    if not os.path.isdir(edinet.xbrl_dir_root):
        os.makedirs(edinet.xbrl_dir_root, exist_ok=True)

    cache_data = yaxbrl_read_cache_data(edinet.cache_file_path)
    edinet.xbrl_get2(edinet.xbrl_dir_root, cache_data, is_exclude_fund)

def yaxbrl_query_get(edinet, start, end, firm, is_exclude_fund):

    cache_data = yaxbrl_read_cache_data(edinet.cache_file_path)
    cache_data = edinet.xbrl_filter_by_dates(cache_data, start, end)
    edinet.xbrl_get_by_query(edinet.xbrl_dir_root, cache_data, firm, is_exclude_fund)

if __name__=="__main__":
    import sys
    import argparse

    cmd_parser = argparse.ArgumentParser(description='Edinet tool')
    cmd_parser.add_argument('--update', nargs='?', const=True, help='update cache data')
    cmd_parser.add_argument('--all', nargs='?', const=True, help='download all avalible data')
    cmd_parser.add_argument('--target', metavar='${target_firm}', type=str, nargs=1, help='get target_firms data')
    cmd_parser.add_argument('--clean', nargs='?', const=True, help='clean local cache ~/.cache/yaxbrl/edinet_cache.json')

    args = cmd_parser.parse_args()

    edinet = EdinetTool()

    edinet.xbrl_dir_root = 'XBRL_raw'
    home_dir = os.path.expanduser('~')
    edinet.cache_dir_path = os.path.join(home_dir, '.cache', 'yaxbrl')
    edinet.cache_file_path = os.path.join(edinet.cache_dir_path, 'edinet_cache.json')
    edinet.base_url = "https://disclosure.edinet-fsa.go.jp/api/v1"

    #excel_file = 'data_j.xls'
    #tickers = edinet.batch_download(excel_file)
    #print(tickers)

    start: datetime = datetime.today()
    end: datetime = start - relativedelta(years=3)
    start = start.date()
    end = end.date()

    print('query ragen over: ', start, end)

    if args.update:
        print("fetching Edinet server")
        yaxbrl_update(edinet, start, end)
        sys.exit(0)

    if args.target:
        print("downloading target xbrl files")

        # only support single frim for this option
        yaxbrl_query_get(edinet, start, end, firm=args.target[0], is_exclude_fund=True)
        sys.exit(0)

    if args.all:
        print("downloading all xbrl files")
        yaxbrl_get(edinet, start, end, is_exclude_fund=True)
        sys.exit(0)

