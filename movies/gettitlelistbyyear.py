import urllib2
from bs4 import BeautifulSoup
import bomojo
import urlparse
import re
import pickle
import httplib
bmj = bomojo.BOMojoScraper()



base_url = "http://www.boxofficemojo.com"
movie_title_list = []
movie_data = []
errorlog = []


for years in range(35):
    valid_page = True
    page_number = 1
    while valid_page:
        url = "http://boxofficemojo.com/yearly/chart/?page="+ str(page_number) +"&view=releasedate&view2=domestic&yr=" + str(2014 - years) + "&p=.htm"
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)

        links = []
        for link in soup.find_all('a'):
            l = link.get('href')
            txt = link.find(text = True)
            if l <> None:
                if '/movies/?id' in l and '#1 Movie:' not in txt:
                    try: 
                        linkclean = l.replace(unichr(160),'%A0')
                        links.append(linkclean.encode('utf-8'))
                    except:
                         print 'could not read %s' % l
                                         
        print len(links)         
        if len(links) == 0:
            break
    
        #skipping first element to avoid #1 movie of the week link
        for link in links:
            titleurl = urlparse.urljoin(base_url,link)
            titleurl = titleurl.replace('page=releases&','')
            try:
                movie_data.append(bmj.parse_full_mojo_page(titleurl))
            except:
                errorlog.append("could not fetch %s" % titleurl)
                print "could not fetch %s" % titleurl
    
        page_number += 1
  

     
    
#print movie_title_list
with open('movie_data_dict_yearly.pkl', 'w') as picklefile:
    pickle.dump(movie_data, picklefile)

with open('movie_data_error_log.pkl', 'w') as picklefile2:
    pickle.dump(errorlog, picklefile2)

print len(movie_data)


