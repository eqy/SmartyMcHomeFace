import nmap
import time
import wifi_greet_rules
import subprocess

TIMEOUT_LIMIT = 600

def scan(nm):
    try:
        return nm.scan(hosts='10.0.0.1/24', arguments='-sn')
    except nmap.nmap.PortScannerError as e:
        print(e)
        return scan(nm)

def get_hosts(scan_results):
    return(scan_results['scan'].keys())

def update_hosts(hosts, cur_hosts):
    time_secs = time.mktime(time.gmtime())
    new_hosts = list()
    for host_ip in cur_hosts:
        if host_ip not in hosts.keys():
            new_hosts.append(host_ip)
        hosts[host_ip] = time_secs
    for host_ip in hosts.keys():
        if time_secs - hosts[host_ip] > TIMEOUT_LIMIT:
            hosts.pop(host_ip)
            print("{0:s} timed out".format(host_ip))
    return new_hosts 

def greet_host(new_host_ip):
    if new_host_ip in wifi_greet_rules.greetmap.keys():
        phrase = wifi_greet_rules.greetmap[new_host_ip]
        print(phrase)
    subprocess.call(['./speech.sh', phrase, '10'])

def main():
    nm = nmap.PortScanner()
    hosts = dict() 
    new_host_queue = list()
    #initialization scan
    cur_hosts = get_hosts(scan(nm))
    update_hosts(hosts, cur_hosts)
    print("Initial hosts: ")
    print(hosts)
    while True:
        cur_hosts = get_hosts(scan(nm))
        new_hosts = update_hosts(hosts, cur_hosts) 
        for new_host_ip in new_hosts:
            print("new host: {0:s}".format(new_host_ip))
            greet_host(new_host_ip)
            

if __name__ == '__main__':
    main()	
