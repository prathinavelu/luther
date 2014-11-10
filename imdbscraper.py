import scraper
import re
import pickle
import urllib2
from collections import defaultdict

class IMDbScraper(scraper.Scraper):

    base_url = 'http://www.imdb.com'
    
    def get_movies_with_keywords(self, keywords_list,sort='moviemeter',type='movie'):
        keys = self.parse_keywords_search(keywords_list)
        key_url = self.base_url+'/search/keyword?keywords='+keys
        page = 1
        nextpage = 'y'
        all_movie_dicts = []
        while nextpage == 'y':
            try:
                list_url = key_url +'&sort='+sort+',asc&mode=advanced&page='+str(page)+'&title_type='+type
                all_movie_dicts = all_movie_dicts + self.scrape_imdb_list(list_url)
                page += 1
            except (TypeError, AttributeError):
                nextpage = 'n'
        return all_movie_dicts
        
        
    def scrape_imdb_list(self, list_url):
        try: 
            soup = self.connect(list_url)
        except:
            print 'connection error!'
            #urlerrors.append(list_url)
            return
        movie_page_list = soup.find('div','lister-list').findChildren('div', 'lister-item mode-advanced')
        dicts = []
        for movie in movie_page_list:
             url = self.base_url + movie.find('a').get('href')
             ref = url.rfind('/')
             clean_url = url[:ref]
             try:
                dicts.append(self.get_movie_data(clean_url))
             except AttributeError:
                pass
        return dicts
    
    
    
    def parse_keywords_search(self, keywords_input):
        keywords_string = ''
        if isinstance(keywords_input,basestring):
            keywords_string = keywords_input.replace(' ','-')
        else:
            for k in keywords_input:
                k_new = k.replace(' ','-')
                if keywords_string  == '':
                    keywords_string = k_new
                else:
                    keywords_string = keywords_string + '%2C' + k_new
        return keywords_string

        
    def get_movie_data(self, movie_page_url, remake='y'):
        movie = {}
        try:
            soup = self.connect(movie_page_url)
        except:
            print 'connection error!'
            #urlerrors.append(movie_page_url)
            return
        
        overview = soup.find(id='overview-top')
        
        try:
            infobar = overview.find('h1').findNextSibling()
            release_details = infobar.find('span','nobr').findChild().text.split('\n')
            movie['release date'] = release_details[0]
            movie['runtime'] = infobar.find('time').text.strip()
        except AttributeError:
             movie['release date'] = None
             movie['runtime'] = None
        title_details = soup.find(id='titleDetails')
        connections = movie_page_url + '/trivia?tab=mc'
        #connections = movie_page_url + '/' + soup.find(id='connections').find('a','nobr').get('href')
        #all_keywords = soup.find("div", {"itemprop": "keywords"})
        try:
            genre = [a.text for a in soup.find("div", {"itemprop": "genre"}).findAll('a')]
        except AttributeError:
            genre = []
        movie['title'] = overview.find('h1').findChild().text
        def find_detail(txt, category):
            try:
                if category == 1:
                    try:
                        gross_url = movie_page_url+'/business'
                        return self.get_gross(gross_url,type=1)
                    except:
                        return title_details.find(text=re.compile(txt)).parent.parent.findAll(text=re.compile('\n'))[1].strip()
                elif category ==2:
                    try:
                        gross_url = movie_page_url+'/business'
                        return self.get_gross(gross_url,type=2)
                    except:
                        return title_details.find(text=re.compile(txt)).parent.parent.findAll(text=re.compile('\n'))[1].strip()
                else:
                    return title_details.find(text=re.compile(txt)).parent.parent.find('a').text
            except AttributeError:
                return None
                
        movie['budget'] = find_detail('Budget:',1)
        movie['gross'] = find_detail('Gross:',2)
        movie['language'] = find_detail('Language:',0)
        movie['country'] = find_detail('Country:',0)
        movie['color'] = find_detail('Color:',0)
        movie['genre'] = genre
        if remake=='y':
            movie['remake'] = self.get_remake_data(connections)
                
        print movie
        return movie
    
    def get_remake_data(self, connections_url):
        try:
            if self.connect(connections_url).find(id='remake_of') == None:
                short_url = self.find_feature_film(self.connect(connections_url).find(id='version_of'))
            else: 
                content = self.connect(connections_url).find(id='remake_of')   
                short_url = content.findNextSibling('div').find('a').get('href')
        except:
            return None
        if short_url != None:
            return self.base_url + short_url
        else:
            return None
        
    
    def get_gross(self, gross_url,type=2):
        content = self.connect(gross_url).find(id='tn15content')
        txt = content.findAll(text=True)
        g = None
        if type==1:
            searchtext = 'Budget'
            length = 6
            for t in txt:
                if t == searchtext and len(t)==length:
                    g = txt[txt.index(t) + 1].split()[0].strip()
                    if '$' not in g:
                        g = None
                    else:
                        g = re.sub("[^0-9]", "", g)
                    break
        if type==2:
            l = [int(re.sub("[^0-9]", "", x.strip())) for x in txt if '(USA)' in x]
            g = max(l)
        print g
        return g
        
    
    def find_feature_film(self,soup):
        s = soup.findNextSibling()
        while s != None:
            s_new = s.findNextSibling()
            if s_new.text.strip().split(')')[1] == '':
                return s_new.find('a').get('href')
            s = s_new
        return None
        
    def add_original_data(self, remakelist):
        list_with_original_data = []
        for movie in remakelist:
            m = movie
            if movie['remake'] != None:
                try:
                    m['remake'] = self.get_movie_data(movie['remake'],remake='n')
                except:
                    m['remake'] = None
            list_with_original_data.append(m)
        return list_with_original_data
        
    def search_movie(self, movie_title, year='n'):
        searchurl = self.base_url+'/find?q=' + movie_title.encode('utf-8').lower().replace(' ','+')
        if year != 'n':
            searchurl += '+(%s)' % year
        try:
            result = self.connect(searchurl).find('table','findList').find('tr')
        except:
            return None
        result_text = result.text.strip().lower()
        result_url = None
        title_length = result_text.find('(')-1
        year_pos = result_text.rfind(')')
        if year != 'n':
            if  result_text[:title_length] == movie_title.strip().lower() and result_text[year_pos-4:year_pos] == str(year):
                url = result.find('a').get('href')
                result_url = self.base_url + url[:url.rfind('/')]
        else:
            title_length = result_text.find('(')-1
            if result_text[:title_length] == movie_title:
                url = result.find('a').get('href')
                result_url = self.base_url + url[:url.rfind('/')]      
        if result_url == None:
            return None
        else:
            print result_url
            return self.get_movie_data(result_url,remake='n')
        
                
        

        
if __name__ == '__main__':
    scraper = IMDbScraper()
    all_remakes = scraper.get_movies_with_keywords(['remake'])
    with open('all_imdb_remakes_new.pkl', 'w') as picklefile:
        pickle.dump(all_remakes, picklefile)
  