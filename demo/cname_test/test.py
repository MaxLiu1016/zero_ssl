import sys
sys.path.append('../..')
from module.dns.dns_pod import create_record
from module.ssl.single_ssl import create_certificate
import concurrent.futures


data_template = {
    "Domain": "hqsmaxtest.online",
    "SubDomain": "test",
    "RecordType": "CNAME",
    "RecordLine": "默认",
    "Value": "test1.hqsmaxtest.online"
}

tasks = [{**data_template, "SubDomain": f"cnametest{i}"} for i in range(10)]

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(create_record, tasks))

# 如果 create_certificate 也是同步的，您可以用同样的方法并发执行它
certificate_tasks = [f"cnametest{i}.hqsmaxtest.online" for i in range(10)]
certificate_results = list(executor.map(create_certificate, certificate_tasks))