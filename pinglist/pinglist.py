import time
from datetime import datetime
from ping3 import ping,verbose_ping

while True:
    with open('pinglist.txt', 'r') as f:
        for line in f.readlines():
            site = line.split('\t')
            if site[0][0] == '#':
                pass
            else:
                result = ping(site[0])
                if result == None:
                    print(site[0] + '\t' + site[1][:-1] + '\t' + ' Ping Check Fail : '+ str(datetime.now())[:19])

                else:
                    print(site[0]+'\t'+site[1][:-1]+'\t'+' Ping Check OK :', '[ Response Time %.2f ] : ' %result+str(datetime.now())[:19])
            time.sleep(1)
        time.sleep(60)