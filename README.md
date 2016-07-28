### LNScan
LNScan(Local Network Scanner)，作为一个内部网络扫描器，仅是为了企业安全自检使用。请不要将本工具用于违法犯罪。本工具结合并部分修改了lijiejie的[BBScan](https://github.com/lijiejie/BBScan)，感谢大牛的分享。


#### Features
* 支持给定ip段或者域名/ip导入
* 抓取title、并检测常见端口，如80, 8080, 6379, 27017等
* 支持多http端口的BBScan扫描

#### Usage

```html
usage: LNScan [options]

A WebScanner to scan local network.
By wps2015(http://wps2015.org)

optional arguments:
  -h, --help   show this help message and exit
  -v           show program's version number and exit
  -f F         import the file of ip/domain list
  --ip IP      ip addresses like 192.168.1.1/24
  --port PORT  user single quotes to split the ports,like 80,21, default 8 ports
```
#### Other
if you have any bug , please remind me in the Issues.
