# usr/bin/env python
# author: wps2015
# coding:utf-8

import requests
import re
import ipaddress
import argparse
import sys
import threading
import Queue
import socket
from libs.result import *


ip_info = {}
start_time = time.time()


def parse_args():
    parser = argparse.ArgumentParser(prog='LNScan',
                                     description="A WebScanner to scan local network.\nBy wps2015(http://wps2015.org)",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage='LNScan [options]')
    parser.add_argument('-v', action='version', version='%(prog)s 1.0 By wps2015')
    parser.add_argument('--ip', metavar='IP', type=str, default='', help='ip addresses like 192.168.1.1/24')
    parser.add_argument('--port', metavar='PORT', type=str, default='', help='user single quotes to split the ports,\
                                          like 80,21, default 8 ports')
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = parser.parse_args()
    _check_args(_args)
    return _args


def _check_args(_args):
    if not _args.ip:
        msg = 'Use --ip to set the ip address range'
        raise Exception(msg)


def ip_parse(ip):
    _ips = ip.strip()
    ips = ipaddress.IPv4Network(u'%s' % _ips, strict=False)
    return ips


class scan(threading.Thread):
    def __init__(self, ipQueue, lock, ports):
        threading.Thread.__init__(self)
        self.ipQueue = ipQueue
        self.lock = lock
        self.ports = ports
        global ip_info

    def run(self):
        while not self.ipQueue.empty():
            url = self.ipQueue.get()
            url = str(url)
            ip_info[url] = {}
            self.http_scan(url)
            self.port_scan(url, self.ports)

    def http_scan(self, url):
        self.lock.acquire()
        print "scanning "+url
        self.lock.release()
        try:
            req = requests.get("http://"+url, timeout=3)
            res_title = re.search(r'<title>([\s\S]*?)</title>', req.text, re.IGNORECASE)
            res_charset = re.search(r'charset=[\"]*?(.*?)\"', req.text, re.IGNORECASE)
            res_h1 = re.search(r'<h1>(.*?)</h1>', req.text, re.IGNORECASE)
            if res_title:
                title = res_title.group(1).strip()
            elif res_h1:
                title = res_h1.group(1).strip()
            else:
                title = "Null"
            if res_charset:
                coding = res_charset.group(1).strip().lower()
                ip_info[url]['title'] = title.encode(coding)
            else:
                ip_info[url]['title'] = title.encode('utf-8')
        except Exception, e:
            ip_info[url]['title'] = ''

    def port_scan(self, url, ports):
        if ports:
            ip_port = ports
        else:
            ip_port = [22, 80, 443, 3389, 6379, 7001, 8080, 27017]
        port_exist = ''

        for port in ip_port:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                self.lock.acquire()
                print "conneting the "+url+':'+str(port)
                self.lock.release()
                sock.connect((url, int(port)))
                print port
                port_exist = port_exist+str(port)+'|'
                sock.close()
            except Exception, e:
                sock.close()
                continue
        sock.close()
        if port_exist:
            ip_info[url]['port'] = port_exist
        else:
            ip_info[url]['port'] = ''


if __name__ == '__main__':
    args = parse_args()
    ip_lists = ip_parse(args.ip)
    ports = args.port
    if ports:
        ports = ports.split(',')
    ipQueue = Queue.Queue()
    threads = []
    lock = threading.Lock()
    for _ip in ip_lists:
        ipQueue.put(str(_ip))
    for i in xrange(20):
        thread = scan(ipQueue, lock, ports)
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()
    report(ip_info, start_time)





