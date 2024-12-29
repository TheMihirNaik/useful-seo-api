from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/analyze-page", methods=["GET"])
def analyze_page():
    page_url = request.args.get('url')
    if not page_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else ""

        # Extract meta description
        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description_tag['content'] if meta_description_tag else ""

        # Extract body text
        body_text = ' '.join([p.get_text() for p in soup.find_all('p')])

        # Extract heading structure
        heading_structure = {}
        for level in range(1, 7):
            tag = f'h{level}'
            headings = [h.get_text() for h in soup.find_all(tag)]
            heading_structure[tag] = headings

        # Extract internal and external links
        internal_links = []
        external_links = []
        domain = urlparse(page_url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(page_url, href)
            if urlparse(full_url).netloc == domain:
                internal_links.append(full_url)
            else:
                external_links.append(full_url)

        # Extract canonical details
        canonical_tag = soup.find('link', rel='canonical')
        canonical = canonical_tag['href'] if canonical_tag else ""

        # Extract meta robots details
        meta_robots_tag = soup.find('meta', attrs={'name': 'robots'})
        meta_robots = meta_robots_tag['content'] if meta_robots_tag else ""

        return jsonify({
            "title": title,
            "meta_description": meta_description,
            "url": page_url,
            "body_text": body_text,
            "heading_structure": heading_structure,
            "internal_links": internal_links,
            "external_links": external_links,
            "canonical": canonical,
            "meta_robots": meta_robots
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch the page", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

