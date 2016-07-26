# !/usr/bin/env python
# coding:utf-8


from report import TEMPLATE_host, TEMPLATE_html, TEMPLATE_info, TEMPLATE_sensitive_path
from string import Template
import webbrowser
import os
import time


def report(scan_result, q_results, start_time):
    print "scanning is over, trying to create the report"
    t_html = Template(TEMPLATE_html)
    t_host = Template(TEMPLATE_host)
    t_info = Template(TEMPLATE_info)
    t_path = Template(TEMPLATE_sensitive_path)

    html_doc = ''
    keys = []
    path_dic = {}
    host_list = []
    while not q_results.empty():                # 处理bbscan的数据
        host, result, severity = q_results.get()
        __host = host.split(':')[0]
        if __host not in host_list:
            host_list.append(__host)
            for key in result.keys():
                path_dic[__host] = result[key]
        else:
            for key in result.keys():
                path_dic[__host] += result[key]
    print path_dic

    for key in scan_result.keys():              # 处理空的字典
        if scan_result[key]['title'] or scan_result[key]['port']:
            keys.append(key)
        else:
            pass
    print keys
    for ke in keys:
        uri = "http://"+ke+'/'
        _str = t_info.substitute({'url': uri, 'title': scan_result[ke]['title'], 'port': scan_result[ke]['port'] })
        if ke in host_list:
            for li in path_dic[ke]:
                _str += t_path.substitute({'status': li['status'], 'url': li['url'] })
        _str = t_host.substitute({'host': ke, 'list': _str})
        html_doc += _str
    cost_time = time.time() - start_time
    cost_min = int(cost_time / 60)
    cost_seconds = '%.2f' % (cost_time % 60)
    html_doc = t_html.substitute({'cost_min': cost_min, 'cost_seconds': cost_seconds, 'content': html_doc})

    report_name = time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.html'
    with open('report/%s' % report_name, 'w') as outFile:
        try:
            outFile.write(html_doc)
        except Exception, e:
            msg = 'trying to encode with gb2312'
            print msg
            outFile.write(html_doc.decode('utf-8', 'ignore').encode('gb2312', 'ignore'))

    print 'Report saved to report/%s' % report_name
    webbrowser.open_new_tab(os.path.abspath('report/%s' % report_name))
