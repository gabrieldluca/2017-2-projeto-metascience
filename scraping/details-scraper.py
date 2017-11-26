from bs4 import BeautifulSoup
import pandas as pd
import requests as rq

MOVIE_DETAILS = pd.read_csv('./data/reviews.csv')['details']
PAGE_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) \
                              AppleWebKit/537.36 (KHTML, like Gecko) \
                              Chrome/51.0.2704.103 \
                              Safari/537.36'}

def extract_details(url):
    global PAGE_HEADER
    response = rq.get(url, headers=PAGE_HEADER)
    parsed_page = BeautifulSoup(response.text, 'html.parser')
    elements = ['a', 'div', 'span', 'table', 'tr']
    tags = ['product_page_title', 'score_description', 
            'metascore_anchor', 'genres', 'languages',
            'product_info', 'credits']
    
    data = {}
    for a in parsed_page.find_all(elements, class_=tags):
        if 'credits' in a.get('class'):
            role = a.find('td', class_='role')
            if role.text.strip() == 'Director':
                director = role.findParent().find('td')
                data['director'] = director.text.strip()
                
        elif 'product_page_title' in a.get('class'):
            data['movie'] = a.text.strip()
        elif 'score_description' in a.get('class'):
            data['acclaim_rate'] = a.find('span').text.strip()
        elif 'metascore_anchor' in a.get('class'):
            data['user_score'] = a.text.strip()
        elif 'genres' in a.get('class'):
            data['genres'] = [i.text for i in a.find_all('span')]
        elif 'languages' in a.get('class'):
            data['languages'] = [i.text for i in a.find_all('span')]
        elif 'product_info' in a.get('class'):
            data['release_date'] = a.find('span', class_=None).text

    if len(data) is not 7: 
        # Has missing data
        if 'languages' not in data.keys(): data['languages'] = []
        if 'director' not in data.keys(): data['director'] = ''
            
    return pd.DataFrame([data], columns=['movie', 'release_date',
                                         'acclaim_rate', 'user_score',
                                         'director', 'genres',
                                         'languages'])


if __name__ == '__main__':
    details = pd.concat(list(map(extract_details, MOVIE_DETAILS)))
    details = details.reset_index(drop=True)
    details.to_csv('./data/details.csv', index=False)