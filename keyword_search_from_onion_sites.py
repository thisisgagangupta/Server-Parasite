import requests
from bs4 import BeautifulSoup

proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

base_url = 'http://tortimeswqlzti2aqbjoieisne4ubyuoeiiugel2layyudcfrwln76qd.onion'
num_pages = 9

keywords = input("Enter keywords to search: ").lower()
keyword_found = False

for page_num in range(1, num_pages + 1):
    url = f'{base_url}/page/{page_num}'
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='home-post')
    for post in posts:
        title = post.find('div', class_='home-post-title').text.lower()
        description = post.find('div', class_='home-post-description').text

        if keywords in title:
            print("\nTitle:", post.find('div', class_='home-post-title').text)
            print("Description:", description.strip())
            keyword_found = True

if not keyword_found:
    print(f"No matching posts found for the keyword '{keywords}' on any page.")
