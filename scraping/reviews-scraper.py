from bs4 import BeautifulSoup
import pandas as pd
import requests as rq

HOME = 'http://www.metacritic.com'
PAGE = 'http://www.metacritic.com/publication/the-new-york-times?num_items=100&page='
DETAILS = '/details'
PAGE_HEADER = {'User-Agent': 'Chrome/63.0'}

def extract_reviews(url):
    global HOME, PAGE_HEADER
    response = rq.get(url, headers=PAGE_HEADER)
    parsed_page = BeautifulSoup(response.text, 'html.parser')
    tags = ['review_actions', 'review_product',
            'review_product_scores', 'review_body']
    
    content = []; data = {}
    for a in parsed_page.find_all('div', class_=tags):
        critscore = a.find('li', class_='brief_critscore')
        date = a.find('li', class_='post_date')
        
        if len(data) is 6:
            data['review_date'] = ''
        if a.find('span', class_='metascore_w'):
            data['metascore'] = a.find('span').text
        if critscore:
            data['review_score'] = critscore.find('span').text
            try: data['reviewer'] = critscore.find('a').text
            except: data['reviewer'] = ''
        if a.findChild() and a.findChild().has_attr('href'):
            data['movie'] = a.find('a').text
            data['details'] = HOME + a.find('a').get('href') + DETAILS
        if a.get('class')[0] == 'review_body':
            data['review_text'] = a.text.strip()
        if date:
            data['review_date'] = date.text[7:]
        
        if len(data) is 7:
            # Store review's information and clean-up
            content.append(data); data = {}
            
    return pd.DataFrame(content, columns=['movie', 'reviewer',
                                          'metascore', 'review_score',
                                          'review_text', 'review_date',
                                          'details'])


if __name__ == '__main__':
    extract_page = lambda num: extract_reviews(PAGE + str(num))
    
    response = rq.get(PAGE+'0', headers=PAGE_HEADER)
    page = BeautifulSoup(response.text, 'html.parser')
    page_num = int(page.find_all('a', class_='page_num')[-1].text)
    
    reviews = pd.concat(list(map(extract_page, range(page_num))))
    reviews = reviews.reset_index(drop=True)
    reviews.to_csv('./data/reviews.csv', index=False)