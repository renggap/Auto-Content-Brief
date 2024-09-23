!pip install nltk
!python -m nltk.downloader punkt
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from collections import Counter
import re
import nltk
from nltk.tokenize import sent_tokenize

# You may need to download NLTK data for tokenization
# nltk.download('punkt')

def google_search(query, num_results=10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='yuRUbf')
    urls = []
    for result in search_results:
        link = result.find('a')
        if link and len(urls) < num_results:
            urls.append(link['href'])
    return urls

def extract_content_structure(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else "No title found"

        # Extract H1, H2, H3 headings only
        headings = [f"{tag.name}: {tag.text.strip()}" for tag in soup.find_all(['h1', 'h2', 'h3'])]

        # Extract meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description['content'] if meta_description else "No meta description found"

        # Extract main content (prioritize <main>)
        main_content = soup.find('main')
        if main_content:
            paragraphs = main_content.find_all('p')
            content = "\n".join([p.text.strip() for p in paragraphs[:5]])  # Limit to first 5 paragraphs
        else:
            content = "Main content section not found"

        # Generate summary based on content preview
        summary = generate_summary(content)

        return {
            "title": title,
            "meta_description": meta_description,
            "headings": headings,  # Only H1, H2, H3 headings
            "content_preview": summary  # Instead of raw content, insert the generated summary
        }
    except Exception as e:
        return {"error": str(e)}

def generate_summary(content):
    if not content or content == "Main content section not found":
        return "No content available to summarize."

    # Tokenize the content into sentences using NLTK
    sentences = sent_tokenize(content)
    
    # Generate summary: take the first 2-3 sentences, which often introduce the main topic
    summary = " ".join(sentences[:3])  # Limit to 2-3 sentences for a concise summary

    return summary if summary else "Unable to generate a meaningful summary."

def main():
    keyword = input("Enter the keyword to search: ")
    urls = google_search(keyword)

    output = f"Search results and content structure for '{keyword}':\n\n"

    for i, url in enumerate(urls, 1):
        output += f"{i}. {url}\n"
        print(f"Crawling {i}/{len(urls)}: {url}")

        structure = extract_content_structure(url)
        output += "   Title: " + structure.get("title", "N/A") + "\n"
        output += "   Meta Description: " + structure.get("meta_description", "N/A") + "\n"
        output += "   Headings:\n"
        for heading in structure.get("headings", []):
            output += f"      {heading}\n"
        output += "   Content Preview:\n" + structure.get("content_preview", "N/A") + "\n\n"

        # Add a delay to be respectful to the servers
        time.sleep(2)

    # Save output to file
    filename = f"{keyword.replace(' ', '_')}_search_results.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nResults have been saved to {filename}")

if __name__ == "__main__":
    main()
