import urllib2
from bs4 import BeautifulSoup
import bomojo
import urlparse
import re
import pickle
import unicodedata
bmj = bomojo.BOMojoScraper()

#url = 'http://www.boxofficemojo.com/movies/?id=elizabeth%A0.htm'
url1 = 'http://www.boxofficemojo.com/movies/?id=darkknight.htm'
url = 'http://www.boxofficemojo.com/yearly/chart/?page=1&view=releasedate&view2=domestic&yr=1998&p=.htm'

page = urllib2.urlopen(url)
soup = BeautifulSoup(page)

links = soup.find_all('a')
for l in links:
    m = l.get('href')
    if m <> None:
        n = 'elizabeth'
        if n in m:
            print m.replace(unichr(160),'%A0')
            
    
    
#.encode('utf-8').replace(' ','%A0')

#print bmj.parse_full_mojo_page(soup)

#print bmj.get_movie_value(soup,'Release Date')
# print bmj.get_movie_value(soup,'Domestic Total')
# print bmj.get_movie_value(soup,'Runtime')
# print bmj.get_movie_value(soup,'Director')

#obj = bmj.get_movie_value(soup,'Opening\xa0Weekend')
#print obj

#obj = soup.find(text=re.compile('Opening\xa0Weekend'))
#print obj
#print not obj
#print obj.find_parent().find_parent().findNextSibling()

# print bmj.get_movie_title(soup)
# 
# 
#print bmj.parse_full_mojo_page(url)
#x = '/movies/?id=elizabeth%A0.htm'
#print x.encode('utf-8')
#y = urlparse.urljoin('http://www.boxofficemojo.com',x.encode('utf-8'))
#print y
#print bmj.parse_full_mojo_page(url1)
    
    

