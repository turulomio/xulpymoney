from datetime import datetime
from urllib.request import urlopen
from json import loads

## Get Github file modification datetime
## https://api.github.com/repos/turulomio/xulpymoney/commits?path=products.xlsx
def get_file_modification_dt(user,project,path):
    url="https://api.github.com/repos/{}/{}/commits?path={}".format(user,project,path)
    bytes_j = urlopen(url).read()
    j=loads(bytes_j.decode('UTF-8'))
    return datetime.strptime(j[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")

if __name__ == '__main__':
    print(get_file_modification_dt("turulomio","xulpymoney","products.xlsx"))