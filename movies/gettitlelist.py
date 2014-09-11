import urllib2
from bs4 import BeautifulSoup
import bomojo
import urlparse
import re
import pickle
bmj = bomojo.BOMojoScraper()



base_url = "http://www.boxofficemojo.com/"
movie_title_list = []
movie_data = []

for i in range(1,6):
    url = "http://boxofficemojo.com/alltime/domestic.htm?page="+ str(i) +"&p=.htm"
    #url = "http://boxofficemojo.com/yearly/chart/?page="+ str(i) +"&view=releasedate&view2=domestic&yr=2014&p=.htm"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    #print soup.find('table')
    #Children = []
    Children = soup.find('table').findNextSibling().findChildren('tr')

    
    for child in Children[6:]:
        titleurl = urlparse.urljoin(base_url,child.find_all('a')[0].get('href'))
        titleurl = titleurl.replace('page=releases&','')
        movie_data.append(bmj.parse_full_mojo_page(titleurl))
        
        #title = child.find('b').text
        #movie_title_list.append(title)
     
    
print movie_title_list
with open('movie_data_dict_new.pkl', 'w') as picklefile:
    pickle.dump(movie_data, picklefile)


print movie_data


