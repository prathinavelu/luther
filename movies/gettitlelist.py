import urllib2
from bs4 import BeautifulSoup
import bomojo
import urlparse
import re
bmj = bomojo.BOMojoScraper()


base_url = "http://www.boxofficemojo.com/"
movie_title_list = []
movie_data = []

for i in range(1,4):
    url = "http://boxofficemojo.com/alltime/domestic.htm?page="+ str(i) +"&p=.htm"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    Children = soup.find('table').findNextSibling().findChildren('tr')
    
    for child in Children[6:]:
        titleurl = urlparse.urljoin(base_url,child.find_all('a')[0].get('href'))
        titleurl = titleurl.replace('page=releases&','')
        movie_data.append(bmj.parse_full_mojo_page(titleurl))
        
        #title = child.find('b').text
        #movie_title_list.append(title)
     
    
#print movie_title_list
print movie_data


