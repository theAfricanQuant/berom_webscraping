from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from pathlib import Path
import json


class WebScraper:
    def __init__(self, url: str, folder: str):
        self.url = url
        self.folder = folder
        self.soup = self.scrape()
        self.chapter = self.soup.find('title').text.replace(" ", "_")

    def scrape(self):
        req = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        url_content = urlopen(req).read()
        return BeautifulSoup(url_content, "lxml")
    
    def clean_div(self, *attribs):
        for tag in self.soup.find_all('span', 
                                 {'class': 'footnote'}):
            tag.decompose()
        for attrib in attribs:
            div_tags = self.soup.find_all('div', class_=attrib)
            for div in div_tags:
                div.decompose()
    
    def clean_subdiv(self, div, att, sub_att):
        parent_div = self.soup.find(div, class_=att) 

        if parent_div:
            subdivision_div = parent_div.find(div, class_=sub_att)  
            if subdivision_div:
                subdivision_div.decompose()

    def clean_text(self):
        self.raw = re.sub(r'\([\d,]+\)|[\[\]]', '', 
                          (self.soup.text
                           .split('©')[0]
                           .split('>')[-1].strip()))
       

    def save_json(self):
        
        # Specify the filename
        json_name = f'{self.chapter}.json'   

        # Create the folder if it doesn't exist
        Path(self.folder).mkdir(parents=True, exist_ok=True)

        # Construct the file path
        json_path = Path(self.folder) / json_name

        data = {}
        matches = re.findall(r'(\d+)\s+([\s\S]*?)(?=\d|$)', self.raw)
        for match in matches:
            key = match[0]
            value = match[1].strip()
            data[key] = value

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        print("JSON data saved to:", json_path)
