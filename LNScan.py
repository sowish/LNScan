# usr/bin/env python
# author: wps2015
# coding:utf-8

import requests
import re
import ipaddress
import argparse
import sys
import time
import socket
import multiprocessing
from libs.result import report
from libs.bbscan import batch_scan


ip_info = {}
next_ips = []
start_time = time.time()


def parse_args():
    parser = argparse.ArgumentParser(prog='LNScan',
                                     description="A WebScanner to scan local network.\nBy wps2015(http://wps2015.org)",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage='LNScan [options]')
    parser.add_argument('-v', action='version', version='%(prog)s 1.0 By wps2015')
    parser.add_argument('-f', type=str, help="import the file of ip/domain list")
    parser.add_argument('--ip', type=str, help='ip addresses like 192.168.1.1/24')
    parser.add_argument('--port', type=str, default='', help='user single quotes to split the ports,\
                                          like 80,21, default 8 ports')
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = parser.parse_args()
    _check_args(_args)
    return _args


def _check_args(_args):
    if not _args.ip and not _args.f:
        msg = 'Use --ip or -f to set the ip address range'
        raise Exception(msg)
    if _args.f and _args.ip:
        raise Exception("one of -f and --ip is available")


def ip_parse(ip):
    _ips = ip.strip()
    ips = ipaddress.IPv4Network(u'%s' % _ips, strict=False)
    return ips


def ip_revive(path):
    ip_ls = []
    with open(path, 'r') as f:
        for ip in f.readlines():
            ip_ls.append(ip.strip())
    return ip_ls


class WeakScan:
    def __init__(self, _host, _ports, _lock):
        self._host = _host
        self.lock = _lock
        self.ports = _ports
        self.ip_result = {}
        self.next_ip = []

    def http_scan(self, url):
        self.ip_result[url] = {}
        try:
            req = requests.get("http://"+url, timeout=3)
            res_title = re.search(r'<title>([\s\S]*?)</title>', req.text, re.IGNORECASE)
            res_charset = re.search(r'charset=[\"]*?(.*?)\"', req.text, re.IGNORECASE)
            res_h1 = re.search(r'<h1>([\s\S]*?)</h1>', req.text, re.IGNORECASE)
            if res_title:
                title = res_title.group(1).strip()
            elif res_h1:
                title = res_h1.group(1).strip()
            else:
                title = "Null"
            if res_charset:
                coding = res_charset.group(1).strip().lower()
                self.ip_result[url]['title'] = title.encode(coding)
            else:
                self.ip_result[url]['title'] = title.encode('utf-8', 'ignore')
        except Exception, e:
            self.ip_result[url]['title'] = ''

    def port_scan(self, url, _ports):
        http_port = [80, 81, 8080, 8081, 8090]
        if _ports:
            ip_port = _ports
        else:
            ip_port = [80, 81, 443, 6379, 7001, 7002, 8080, 8081, 11211, 27017]
        port_exist = ''
        self.lock.acquire()
        print "connecting ", url
        self.lock.release()
        for port in ip_port:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((url, int(port)))
                if int(port) in http_port:
                    _host = url+':'+str(port)
                    if _host not in self.next_ip:
                        self.next_ip.append(_host)
                port_exist = port_exist+str(port)+'|'
                sock.close()
            except Exception, e:
                sock.close()
                continue
        if port_exist:
            self.ip_result[url]['port'] = port_exist
        else:
            self.ip_result[url]['port'] = ''

    def s_scan(self):
        self.http_scan(self._host)
        self.port_scan(self._host, self.ports)
        return self.ip_result, self.next_ip


def scan(url, s_results, _ports, _lock):
    b = WeakScan(url, _ports, _lock)
    _results, _hosts = b.s_scan()
    if _results:
        for key in _results.keys():
            _lock.acquire()
            print key, _results[key]['port']
            _lock.release()
        s_results.put((_results, _hosts))


if __name__ == '__main__':
    args = parse_args()
    if args.ip:
        ip_lists = ip_parse(args.ip)
    else:
        ip_lists = ip_revive(args.f)
    ports = args.port
    if ports:
        ports = ports.split(',')

    ip_Queue = multiprocessing.Manager().Queue()   # start port and title scan
    locks = multiprocessing.Manager().Lock()
    pools = multiprocessing.Pool(20)
    for _ip in ip_lists:
        pools.apply_async(func=scan, args=(str(_ip), ip_Queue, ports, locks,))
    pools.close()
    pools.join()
    while not ip_Queue.empty():
        s_results, s_hosts = ip_Queue.get()
        ip_info = dict(ip_info, **s_results)
        next_ips += s_hosts

    q_results = multiprocessing.Manager().Queue()   # start BBScan
    lock = multiprocessing.Manager().Lock()
    pool = multiprocessing.Pool(10)
    scanned_ips = []
    for _host in next_ips:
        pool.apply_async(func=batch_scan, args=(_host, q_results, lock, 20, 20))
    pool.close()
    pool.join()
    report(ip_info, q_results, start_time)






