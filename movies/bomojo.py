import sys
import re
import urllib2
import scraper
from bs4 import BeautifulSoup
import dateutil.parser
import urlparse

class BOMojoScraper(scraper.Scraper):

    base_url = "http://www.boxofficemojo.com/"
    search_url = base_url + "search/?q=%s"

    def full_movie_dict_from_title(self,movie_name):
        return self.parse_full_mojo_page(self.get_full_page_url_from_title(movie_name))

    def get_full_page_url_from_title(self,movie_name):
        search_soup = self.search(movie_name)
        found_matches = search_soup.find(text=re.compile("Movie Matches"))
        if found_matches:
            matches_table = found_matches.parent.find_next_sibling("table")
            result_rows = matches_table.find_all('tr')
            all_matches = []
            for row in result_rows:
                all_matches.append(row.find('a'))
            full_page_url = None
            for match in all_matches:
                if match.text.lower().strip() == movie_name.lower().strip():
                    full_page_url = urlparse.urljoin(self.base_url, match['href'])
            if full_page_url is None:
                    full_page_url = urlparse.urljoin(self.base_url, all_matches[0]['href'])
            return full_page_url

        # if we end up here without returning anything, we did not hit a match
        log_message = "[LOG: No match found for %s]" % movie_name
        print >> sys.stderr, log_message
        return -1


    def parse_full_mojo_page(self,full_page_url):
        soup = self.connect(full_page_url)
        release_date = self.to_date(
            self.get_movie_value(soup,'Release Date'))
        domestic_total_gross = self.money_to_int(
            self.get_movie_value(soup,'Domestic Total'))
        runtime = self.runtime_to_minutes(self.get_movie_value(soup,'Runtime'))
        director = self.get_movie_value(soup,'Director')
        rating = self.get_movie_value(soup,'MPAA Rating')

        movie_dict = {
            'movie title':self.get_movie_title(soup),
            'release date':release_date,
            'domestic_total_gross':domestic_total_gross,
            'runtime':runtime,
            'director':director,
            'rating':rating
        }

        return movie_dict
            

    def get_movie_value(self,soup,value_name):
        '''
        takes a string attribute of a movie on the page and 
        returns the string in the next sibling object (the value for that attribute)
        '''
        
        obj = soup.find(text=re.compile(value_name))
        #print 'get_movie_value obj', obj
        if not obj: 
            return None
    
        #for domestic box office totals
        if value_name == 'Domestic Total':
            return obj.find_parent('td').find('b').text.split(' ')[0]
            
        # this works for most of the values
        next_sibling = obj.findNextSibling()
        if next_sibling:
            return next_sibling.text

        # this next part works for the director
        elif obj.find_parent('tr'):
            sibling_cell = obj.find_parent('tr').findNextSibling()
            if sibling_cell:
                return sibling_cell.text
                
        else:
            return -1


    def get_movie_title(self,soup):
        title_tag = soup.find('title')
        movie_title = title_tag.text.split('(')[0].strip()
        return movie_title
    
    def to_date(self,datestring):
        return dateutil.parser.parse(datestring)

    def money_to_int(self,moneystring):
        return int(moneystring.replace('$','').replace(',',''))

    def runtime_to_minutes(self,runtimestring):
        rt = runtimestring.split(' ')
        return int(rt[0])*60 + int(rt[2])
