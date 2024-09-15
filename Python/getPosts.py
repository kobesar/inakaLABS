import os
import requests as re
import pandas as pd
import time
import random

from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

keywords_df = pd.read_csv('https://raw.githubusercontent.com/kobesar/inakaLABS/main/Data/Keywords.csv')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
SEARCH_TOOL_ID = os.getenv('SEARCH_TOOL_ID')

base_url = 'https://www.googleapis.com/customsearch/v1?key=%s' % GOOGLE_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

system_instruction = """
You are a content creator for Inaka LABS, a groundbreaking initiative brought to you by the Future Economic Rural Network (FERN), aimed at unleashing the untapped potential of rural Japan through the development of rural startup hubs. We believe in a future where rural areas flourish with technology, innovation, and entrepreneurial spirit, contributing significantly to Japan’s economic diversity and sustainability.

Your job is to create a post given an article, follow the given formula to create a post:

1. Article summary
2. Hot take: this is how our approach is different/more interesting/better
3. Call to action

Combine the summary, hot take and call to action in a single continuous paragraph. Add relevant hashtags along with a #inakaLABS at the end. All under 280 characters.
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

# Function to generate post, given some text
def generate_post(text):
    response = model.generate_content(
    text,
        safety_settings={
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    })
    
    return response

# Grab all the sites from the query
def get_sites(category, term, dateRestrict='d7'):
  # Build exactTerms to search for
  exactTerms = ','.join(['japan', term])

  # Other terms to search for
  orTerms = category

  # Combine the base_url with the custom query
  url = base_url + '&cx=%s&exactTerms=%s&orTerms=%s&dateRestrict=%s' % (SEARCH_TOOL_ID, exactTerms, orTerms, dateRestrict)
  
  result = []

  response = re.get(url)
  json = response.json()

  if 'items' in json.keys():
    for item in json['items']:
      post = generate_post(item['snippet'])

      result.append({
        'category': category,
        'term': term,
        'title': item['title'],
        'link': item['link'],
        'formattedUrl': item['formattedUrl'],
        'snippet': item['snippet'],
        'publishedDate': item['pagemap']['metatags'][0]['article:published_time'] if 'pagemap' in item.keys() and 'article:published_time' in item['pagemap']['metatags'][0] else None,
        'scrapeDate': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'post': post.text
      })
      
    return result
  else:
    return []
  
full_result = []

for index, row in keywords_df.sample(25).iterrows():
  category = row['Category Clean']
  term = row['Keyword Clean']
  
  full_result += get_sites(category, term)

  time.sleep(1)

pd.DataFrame(full_result).to_csv('Runs/data/query_results_' + time.strftime('%Y%m%d', time.localtime()) + '.csv', index=False)