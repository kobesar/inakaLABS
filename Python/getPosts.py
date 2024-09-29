import os
import requests as re
import pandas as pd
import time
from datetime import datetime

# Import the Google's generative AI library
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold, GenerationConfig

# Load the keywords
keywords_df = pd.read_csv('https://raw.githubusercontent.com/kobesar/inakaLABS/main/Data/Keywords.csv')

# Load the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
cx = os.getenv('SEARCH_TOOL_ID')

# Ccnfigure base URL for Search API
base_url = 'https://www.googleapis.com/customsearch/v1?key=%s' % GOOGLE_API_KEY

# Set API key for Gemini
genai.configure(api_key=GEMINI_API_KEY)

# System instruction for general model
system_instruction = """
You are a content creator for Inaka LABS, a groundbreaking initiative brought to you by the Future Economic Rural Network (FERN), aimed at unleashing the untapped potential of rural Japan through the development of rural startup hubs. We believe in a future where rural areas flourish with technology, innovation, and entrepreneurial spirit, contributing significantly to Japan’s economic diversity and sustainability.

Your job is to create an opioniated post given the title and snippet of an article, follow the given formula to create a post. Cater the post to an audience on Linkedin, Facebook, and Instagram. Follow the given formula to create a post:

1. Article summary
2. Hot take: this is how our approach is different/more interesting/better
3. Call to action

Combine the summary, hot take and call to action in a single continuous paragraph. Add relevant hashtags along with a #inakaLABS at the end, in a regular text format. Remove any Markdown formatting.
"""

# System instruction for model to generate X specific posts
system_instruction_x = """
You are a content creator for Inaka LABS, a groundbreaking initiative brought to you by the Future Economic Rural Network (FERN), aimed at unleashing the untapped potential of rural Japan through the development of rural startup hubs. We believe in a future where rural areas flourish with technology, innovation, and entrepreneurial spirit, contributing significantly to Japan’s economic diversity and sustainability.

Your job is, in a single sentence, create a short and opionated post given the title and snippet of an article. Cater the post for an audience on X. Follow the given formula to create a post:

Starting with a hot take (this is how our approach is different/more interesting/better) and a call to action. Include relevant hashtags along with a #inakaLABS. Remove any Markdown formatting.
"""

# Initialize the models
model_general = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
model_x = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction_x)

# Generation Config
config = GenerationConfig(
    max_output_tokens=2048, temperature=0.4
)
config_x = GenerationConfig(
    max_output_tokens=60, temperature=0.4, top_k=50
)

def remove_markdown(text):
    """
    This function removes markdown formatting from the input text.

    Parameters:
    text (str): The text with markdown formatting.

    Returns:
    str: The text with markdown removed.
    """
    # Remove headers (e.g., ## Header, # Header)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove emphasis (bold, italics, etc.)
    text = re.sub(r'(\*{1,2}|_{1,2})(.*?)\1', r'\2', text)
    
    # Remove links and images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Removes images
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)   # Removes links
    
    # Remove inline code and code blocks
    text = re.sub(r'(`{1,3})(.*?)\1', r'\2', text)
    
    # Remove blockquotes
    text = re.sub(r'^\>\s*', '', text, flags=re.MULTILINE)
    
    # Remove strikethrough
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    
    # Remove unordered list bullets (*, +, -)
    text = re.sub(r'^(\*|\+|\-)\s+', '', text, flags=re.MULTILINE)
    
    # Remove ordered list numbers (e.g., 1., 2., 3.)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***)
    text = re.sub(r'^(-{3,}|_{3,}|\*{3,})$', '', text, flags=re.MULTILINE)
    
    # Remove extra spaces
    text = re.sub(r'\n{2,}', '\n', text)  # Normalize multiple newlines to one
    
    return text.strip()

# Function to generate post, given some text
def generate_post(title, snippet, model, config):
    response = model.generate_content(
      'Title: %s \n Snippet: %s' % (title, snippet),
      safety_settings={
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        },
      generation_config=config
    )

    time.sleep(4.5)

    # print('Post Generated.')
    
    return response

# Grab all the sites from the query
def get_sites(category, term, dateRestrict='d7'):
  # Build exactTerms to search for
  exactTerms = ','.join(['japan', term])

  # Other terms to search for
  orTerms = category

  # Combine the base_url with the custom query
  url = base_url + '&cx=%s&exactTerms=%s&orTerms=%s&dateRestrict=%s' % (cx, exactTerms, orTerms, dateRestrict)
  
  result = []

  response = re.get(url)
  json = response.json()

  # print(json)

  if 'items' in json.keys():
    for item in json['items']:
      post_general = generate_post(item['title'], item['snippet'], model_general, config)
      post_x = generate_post(item['title'], item['snippet'], model_x, config_x)

      result.append({
        'category': category,
        'term': term,
        'title': item['title'],
        'link': item['link'],
        'formattedUrl': item['formattedUrl'],
        'snippet': item['snippet'],
        'publishedDate': item['pagemap']['metatags'][0]['article:published_time'] if 'pagemap' in item.keys() and 'metatags' in item['pagemap'].keys() and 'article:published_time' in item['pagemap']['metatags'][0] else None,
        'scrapeDate': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'post_general': remove_markdown(post_general.text),
        'post_x': remove_markdown(post_x.text)
      })
      
    return result
  else:
    return []
  
full_result = []

for index, row in keywords_df.sample(50).iterrows():
  category = row['Category Clean']
  term = row['Keyword Clean']
  
  full_result += get_sites(category, term)

pd.DataFrame(full_result).to_csv('Data/Runs/query_results_' + time.strftime('%Y%m%d', time.localtime()) + '.csv', index=False)
