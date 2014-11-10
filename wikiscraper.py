import scraper
import re
import pickle
import urllib2
from collections import defaultdict
from imdbscraper import IMDbScraper

imdbscraper = IMDbScraper()


class WikiScraper(scraper.Scraper):

    base_url = 'http://en.wikipedia.org'
    
    def get_movie_data(self, movie_page_url):
        """
        creates a dictionary of attributes from an individual movie's wikipedia page
        """
        main_wiki_content  = self.connect(movie_page_url).find(id="mw-content-text")
        try:
            all_fields = main_wiki_content.find('table', 'infobox vevent').find_all('th')
            movie_dict = {'Title': all_fields[0].text}
            print all_fields[0].text
            for field in all_fields[1:]:
                movie_dict[field.text] = field.findNextSibling().text            
        except (IndexError, AttributeError):
            i = movie_page_url.rfind('/')
            movie_dict = {'Title': movie_page_url[i+1:]}        
        return defaultdict(str, movie_dict)
    
    
    def get_remake_dict_pairs(self, list_page_url):
        """
        from a wikipedia list of remake-original pairs, creates a list of dictionary pairs
        """
        main_wiki_content  = self.connect(list_page_url).find(id="mw-content-text")
        base_url = self.base_url
        remake_original_pairs = []
        
        for table in main_wiki_content.find_all("table"):
            for row in table.findChildren('tr')[1:]:
                try:
                    original_url = base_url + row.findChildren('td')[1].find('a').get('href')
                except AttributeError:
                #   try imdb search
                    pass
                    
                for value in row.findChildren('td')[0].find_all('i'):
                    try:
                        remake_url = base_url + value.find('a').get('href')
                    except AttributeError:
                        pass
                 
                    print original_url
                    try:
                        remake_original_pairs.append(
                                [self.get_movie_data(original_url),
                                 self.get_movie_data(remake_url)])
                    except urllib2.HTTPError:
                        pass                   
        return remake_original_pairs
        
    def clean_release_date(self, date):
        clean_date = date.split()
        for d in clean_date:
            if len(d)==4:
                try:
                    clean_date = int(d)
                    break
                except:
                    pass 
        return clean_date
        
    def get_imdb_data(self, wikipairlist):
        newlist = []            
        for w in wikipairlist:
            remake_dict = w[1]                
            remake_title = remake_dict['Title']
            remake_date = self.clean_release_date(remake_dict['Release dates']) 
            if remake_date == []:
                remake_imdb = imdbscraper.search_movie(remake_title)
            else:
                remake_imdb = imdbscraper.search_movie(remake_title, year=remake_date)
            if remake_imdb != None:
                newlist.append(remake_imdb)
        return newlist
                
                
        
    
def main(urllist):
    dict_pairs =[]
    scraper = WikiScraper()
    for url in urllist:
        dict_pairs= dict_pairs + scraper.get_remake_dict_pairs(url)
    #with open('movie_remake_data_pairs.pkl', 'w') as picklefile:
    #    pickle.dump(dict_pairs, picklefile)
    with open('all_wiki_data_pairs.pkl', 'w') as picklefile:
        pickle.dump(dict_pairs, picklefile)
        
if __name__ == '__main__':
    #urllist = ['http://en.wikipedia.org/wiki/List_of_film_remakes_(A%E2%80%93M)', 
    #           'http://en.wikipedia.org/wiki/List_of_film_remakes_(N%E2%80%93Z)']
               
    urllist = ['http://en.wikipedia.org/wiki/List_of_film_remakes_(A%E2%80%93M)', 
               'http://en.wikipedia.org/wiki/List_of_film_remakes_(N%E2%80%93Z)',
              'http://en.wikipedia.org/wiki/List_of_English-language_films_with_previous_foreign-language_film_versions']
    
    #urllist = ['http://en.wikipedia.org/wiki/List_of_English-language_films_with_previous_foreign-language_film_versions']
               
    main(urllist)


       



