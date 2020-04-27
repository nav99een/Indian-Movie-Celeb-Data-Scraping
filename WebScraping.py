#!/usr/bin/env python
# coding: utf-8

# ### Importing Librabries

# In[41]:


from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import urllib
import re
from urllib.request import urlopen

from PIL import Image
from io import StringIO

driver = webdriver.Chrome('/opt/google/chrome/chromedriver')
base_url = "https://www.imdb.com/"

Names = []


# ### Defining Utility Function

# #### To Remove extra spaces

# In[36]:


def basic_prep(text):
    return re.sub('\n','',str(text)).strip()


# #### Retrieval of First Page

# In[37]:


#Returns list data containing infromation of all Celeb on given page
def find_base_page(url="https://www.imdb.com/list/ls002913270/"):
    driver.get(url)
    print("loading page")
    content = driver.page_source
    soup = BeautifulSoup(content)
    actors = []
    for div in soup.findAll('div', attrs={'class':'lister-item mode-detail'}):
        for item in div.findAll('div',attrs={'class':'lister-item-content'}):
            p = (item.find('h3')).find('a', href=True)
            name = p.text
            print("Loading page for"+name)
            second_page_link = base_url+p["href"]
            try:
                s = second_page(second_page_link)
                last_page_link = base_url+s
                #print(last_page_link)
                content = last_page(last_page_link)
                content['name'] = name
            except:
                continue
            actors.append(content)
        #to extract images of the celeb    
        for img in div.findAll('img'):
            url = img.get('src')
            ext = url.split('.')[-1]
            path = "images/"+name+"."+ext
            urllib.request.urlretrieve(url, path)
    return actors


# #### Retrival of Second Page

# In[38]:


#Returns link to the next page where bio of celeb is placed
def second_page(url):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content)
    p = soup.find('span',attrs={'class':'see-more inline nobr-only'})
    #print(p)
    return p.find('a', href=True)["href"]


# In[39]:


#Returns a dictionary containing data of Celeb
def last_page(url): 
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content)
    about = soup.find_all('div', class_='soda odd')[0].find_all('p')[0].text
    about = basic_prep(about)
    trademarks = []
    s = 0
    try:
        t = soup.find_all('h4', class_='li_group')[3]
        text = t.text
        if('Trade' in str(text)):
            s = int(re.findall('[0-9]+',t.text)[0])
        else:
            t = soup.find_all('h4', class_='li_group')[2]
            text = t.text
            if('Trade' in str(text)):
                s = int(re.findall('[0-9]+',t.text)[0])
    except:
        pass
    odd = True
    i = 1
    j = 1
    #print(s)
    for k in range(s):
        if(odd):
            odd = False
            text = soup.find_all('div', class_='soda odd')[i].text
            trademarks.append(basic_prep(text))
            i+=1
        else:
            odd = True
            text = soup.find_all('div', class_='soda odd')[i].text
            trademarks.append(basic_prep(text))
            #trademarks.append(soup.find_all('div', class_='soda even')[j].text)
            j+=1
    #print(trademarks)
    trivias = []

    p = 3
    for k in range(p):
        try:
            text1 = soup.find_all('div', class_='soda odd')[k+i].text
            text2 = soup.find_all('div', class_='soda even')[j+k].text
            #trivias.append(soup.find_all('div', class_='soda odd')[k+i].text)
            #trivias.append(soup.find_all('div', class_='soda even')[j+k].text)
            trivias.append(basic_prep(text1))
            trivias.append(basic_prep(text2))
        except:
            pass

    d = dict()
    d['about'] = about
    d['trademark'] = trademarks
    d['trivia'] = trivias

    return d


# In[40]:


def main():
    return find_base_page()


# In[ ]:


n = main()


# In[ ]:


#Converting into DataFrame
df = pd.DataFrame(n)
df.head()


# In[ ]:


l = []
for i in range(1,len(df)+1):
    l.append(i)
df['id'] = l


# In[ ]:


df = df[['id','name','about','trademark', 'trivia']]
df.columns = ['id','Name', 'About', 'TradeMark', 'Trivia']
df.head()


# In[ ]:


#Dumping data into csv
df.to_csv('new_scraped_data.csv')


# In[ ]:


# Dumping data into SQL Database
import sqlite3

conn = sqlite3.connect('TestDB1.db')
c = conn.cursor()

c.execute('CREATE TABLE Celeb (id INTEGER PRIMARY KEY, Name text, About text, TradeMark text, Trivia text)')
conn.commit()


#df = pd.read_csv('new_scraped_data.csv')
df.to_sql('Celeb', conn, if_exists='replace', index = False)
 
c.execute('''  
SELECT * FROM Celeb
          ''')

for row in c.fetchall():
    print (row)


# In[ ]:




