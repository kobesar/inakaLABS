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
cx = os.getenv('SEARCH_TOOL_ID')

print(GOOGLE_API_KEY)
print(GEMINI_API_KEY)
print(cx)


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

response = model.generate_content(
'Hello this is a test',
    safety_settings={
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
})

print(response.text)