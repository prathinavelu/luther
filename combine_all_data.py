from imdbscraper import IMDbScraper
import pickle
import re

scraper = IMDbScraper()



        
def clean_imdb(imdb):
    imdb_new = imdb        
    for i in imdb_new:
        try:
            i['budget'] = clean_imdb_box_office(i['budget'])
            i['gross'] = clean_imdb_box_office(i['gross'])
            i['release date'] = clean_imdb_box_office(i['release date'])

            if i['remake'] != None:
                i['remake']['budget'] = clean_imdb_box_office(i['remake']['budget'])
                i['remake']['gross'] = clean_imdb_box_office(i['remake']['gross'])  
                i['remake']['release date'] = clean_imdb_box_office(i['remake']['release date'])
        except:
            pass
    return imdb_new
    
def clean_wiki_date(date):
    clean_date = date.split()
    for d in clean_date:
        if len(d)==4:
            try:
                clean_date = int(d)
                break
            except:
                pass 
    return clean_date

        
def clean_imdb_date(fulldate):
    try:
        d = fulldate.strip()
        return d[-4:]
    except:
        return None
    
def clean_imdb_box_office(amt):
    if '$' in amt:
        try:
            return re.sub("[^0-9]", "", amt)
            #return amt.strip().replace('$','').replace(',','')
        except AttributeError:
            return None
    else:
        return None
    
    
if __name__ == '__main__':

    with open('all_imdb_remakes_new.pkl','rb') as infile:
        imdb_list = pickle.load(infile)
        
    imdb_data = scraper.add_original_data(imdb_list)
    
#     with open('complete_imdb_remakes_new.pkl','rb') as infile:
#         imdb_data = pickle.load(infile)
        
    with open('all_wiki_data_pairs.pkl','rb') as infile:
        wiki_data = pickle.load(infile) 
        
    all_data = []
     
    #new_imdb= clean_imdb(imdb_data)
    wd = wiki_data

    clean_wiki = []
    for i in wd:
        o_title = i[0]['Title'].strip().split('(')[0].replace('_',' ')
        o_year = clean_wiki_date(i[0]['Release dates'])
        print o_title
        movie_original = scraper.search_movie(o_title,o_year)
        r_title = i[1]['Title'].strip().split('(')[0].replace('_',' ')
        r_year = clean_wiki_date(i[1]['Release dates'])
        print r_title
        movie_remake = scraper.search_movie(r_title,r_year)
        try:
            movie_remake['remake'] = movie_original
        except TypeError:
            pass
        clean_wiki.append(movie_remake)
    
    #new_wiki = clean_imdb(clean_wiki)
    
    all_data = imdb_data + clean_wiki
    
    with open('all_movie_data_combined_new.pkl', 'w') as picklefile:
        pickle.dump(all_data, picklefile)