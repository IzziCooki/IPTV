from flask import Flask, render_template, request
import requests

app = Flask(__name__)

class IPTVManager:
    def __init__(self):
        self.base_url = "https://iptv-org.github.io/api"
        self.streams = []
        self.channels = {}
        self.categories = {}

    def load_data(self):
        """Fetches and filters data for US channels only."""
        print("Fetching latest data for US channels... (this may take a moment)")
        try:
            # Fetch all available categories
            category_res = requests.get(f"{self.base_url}/categories.json")
            self.categories = {cat['id']: cat['name'] for cat in category_res.json()}

            # Fetch all channels
            channel_res = requests.get(f"{self.base_url}/channels.json")
            all_channels = channel_res.json()

            # Filter for US channels and store them
            us_channel_ids = set()
            for c in all_channels:
                if c.get('country') == 'US':
                    us_channel_ids.add(c['id'])
                    self.channels[c['id']] = c

            # Fetch all streams
            stream_res = requests.get(f"{self.base_url}/streams.json")
            all_streams = stream_res.json()

            # Filter streams to only include those from US channels
            self.streams = [s for s in all_streams if s.get('channel') in us_channel_ids]
            
            print(f"Loaded {len(self.streams)} streams from {len(self.channels)} US channels.\n")

        except Exception as e:
            print(f"Error loading data: {e}")

    def get_categories(self):
        """Returns a sorted list of unique category names from loaded channels."""
        found_categories = set()
        for channel in self.channels.values():
            for cat_id in channel.get('categories', []):
                if cat_id in self.categories:
                    found_categories.add(self.categories[cat_id])
        return sorted(list(found_categories))

    def search(self, query, category=None):
        """Searches streams by title, optionally filtering by category."""
        query = query.lower()
        results = []

        # First, filter by category if one is provided
        streams_to_search = []
        if category:
            cat_id_to_find = None
            for cid, cname in self.categories.items():
                if cname.lower() == category.lower():
                    cat_id_to_find = cid
                    break
            
            if cat_id_to_find:
                for s in self.streams:
                    channel_info = self.channels.get(s.get('channel'), {})
                    if cat_id_to_find in channel_info.get('categories', []):
                        streams_to_search.append(s)
            else:
                return [] # No streams if category doesn't exist
        else:
            streams_to_search = self.streams

        # Then, search by title within the filtered list
        for s in streams_to_search:
            title = (s.get('channel') or '').lower()
            if query in title:
                results.append({
                    'title': self.channels.get(s.get('channel'), {}).get('name', 'Unknown Channel'),
                    'url': s.get('url'),
                    'quality': s.get('height', 'N/A')
                })
        
        return results

iptv = IPTVManager()
iptv.load_data()
available_categories = iptv.get_categories()

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    search_query = ""
    selected_category = ""

    if request.method == 'POST':
        selected_category = request.form.get('category')
        search_query = request.form.get('search', '')
        results = iptv.search(search_query, category=selected_category)
    
    return render_template('index.html', 
                           categories=available_categories, 
                           results=results,
                           selected_category=selected_category,
                           search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True)
