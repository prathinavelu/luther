from scraper import Scraper
import re
import pickle
from collections import defaultdict

def getconnections(movielist):
    newlist = movielist
    newnewlist = []
    for m in newlist:
        n = m
        try:
            n['remake']['connections'] = search_movie(m['remake']['title'],m['remake']['year'])
        except:
            try:
            pass
        newnewlist.append(n)
    return newnewlist
        

base_url = 'http://www.imdb.com'
scraper = Scraper()

def search_movie(movie_title,year='n'):
    searchurl = base_url+'/find?q=' + movie_title.encode('utf-8').lower().replace(' ','+')
    if year != 'n':
        searchurl += '+(%s)' % year
    try:
        result = scraper.connect(searchurl).find('table','findList').find('tr')
    except:
        return defaultdict(int)
    result_text = result.text.strip().lower()
    result_url = None
    title_length = result_text.find('(')-1
    year_pos = result_text.rfind(')')
    if year != 'n':
        if result_text[:title_length] == movie_title.strip().lower() and result_text[year_pos-4:year_pos] == str(year):
            url = result.find('a').get('href')
            result_url = base_url + url[:url.rfind('/')]
    else:
        title_length = result_text.find('(')-1
        if result_text[:title_length] == movie_title:
            url = result.find('a').get('href')
            result_url = base_url + url[:url.rfind('/')]      
    if result_url == None:
        return defaultdict(int)
    else:
        return connection_search(result_url)
            
def connection_search(url):
    connectionsurl = url+ '/trivia?tab=mc'
    d = defaultdict(int)
    try:
        soup = scraper.connect(connectionsurl)
    except:
        return defaultdict(int)
    try:
        c = soup.find('div','jumpto').findAll(text=True)
    except:
        return defaultdict(int)
    l = [x for x in c[1:] if x != '|' and x != '\n']
    while len(l)>0:
        d[l[0]] = int(re.sub("[^0-9]", "", l[1]))
        l = l[2:]
    print connectionsurl
    return d
    
if __name__ == "__main__":
    with open('movielist_final.pkl','rb') as infile:
        movies_final = pickle.load(infile)
    
    with_connections = getconnections(movies_final)
    
    with open('movies_final_with_connections.pkl', 'w') as picklefile:
        pickle.dump(with_connections, picklefile)
        
    
    