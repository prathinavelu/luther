from bs4 import BeautifulSoup
import urllib2

#despite url, has all cpi through 2014
url = 'http://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)


def get_cpi_values():
 
    table=soup.find('table')
    rows = table.findChildren('tr')
    cpi_dict = {}

    for r in rows[2:]:
        year = r.find('td')
        cpi = year.findNextSibling()
        cpi_dict[int(year.text)] = float(cpi.text)
    return cpi_dict
    
def inflation(oldyear, newyear=2014, amt=1):
    cpi = get_cpi_values()
    inflation = (cpi[newyear] - cpi[oldyear])/cpi[oldyear] + 1
    return inflation*amt 
    
    
if __name__ == '__main__':
    print get_cpi_values()
    print inflation(1980)