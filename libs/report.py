# -*- encoding: utf-8 -*-

TEMPLATE_html = """
<html>
<head>
<title>LNScan Report</title>
<meta http-equiv="content-type" content="text/html;charset=UTF-8">
<style>
    body {width:960px; margin:auto; margin-top:10px; background:rgb(200,200,200);}
    p {color: #666;}
    h2 {color:#002E8C; font-size: 1em; padding-top:5px;}
</style>
</head>
<body>
<p>Please consider to contribute some rules to make LNScan more efficient.  <b>LNScan v 1.0</b></p>
<p>Current Scan was finished in ${cost_min} min ${cost_seconds} seconds.</p>
${content}
</body>
</html>
"""

TEMPLATE_host = """
<h2>${host}</h2>
<ul>
${list}
</ul>
"""

TEMPLATE_info = """
 <li class="normal"><a href="${url}" target="_blank">${title}</a></li><br/>
 <li style=“color:#F00" class="high"><p>${port}</p></li>
"""

TEMPLATE_sensitive_path = """
 <li class="normal">[${status}] <a href="${url}" target="_blank">${url}</a></li>
"""

