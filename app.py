from flask import Flask, render_template, request, abort, redirect, url_for
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

class IPTVManager:
    def __init__(self):
        self.base_url = "https://iptv-org.github.io/api"
        self.channels = {} # id -> channel_obj
        self.streams = {}  # channel_id -> list of streams
        self.categories = {} # id -> category_obj
        self.countries = {} # code -> country_obj
        self.languages = {} # code -> language_obj
        self.data_loaded = False

    def load_data(self):
        """Fetches all necessary data from the API."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting data load...")
        
        try:
            # 1. Load Categories
            print(" - Fetching Categories...")
            cat_res = requests.get(f"{self.base_url}/categories.json")
            self.categories = {c['id']: c for c in cat_res.json()}

            # 2. Load Countries
            print(" - Fetching Countries...")
            country_res = requests.get(f"{self.base_url}/countries.json")
            self.countries = {c['code']: c for c in country_res.json()}

            # 3. Load Channels (This is large)
            print(" - Fetching Channels...")
            chan_res = requests.get(f"{self.base_url}/channels.json")
            all_channels = chan_res.json()
            # Index channels by ID
            self.channels = {c['id']: c for c in all_channels}

            # 4. Load Streams (This is large)
            print(" - Fetching Streams...")
            stream_res = requests.get(f"{self.base_url}/streams.json")
            all_streams = stream_res.json()
            
            # Index streams by channel ID for fast lookup
            self.streams = {}
            for s in all_streams:
                c_id = s.get('channel')
                if c_id:
                    if c_id not in self.streams:
                        self.streams[c_id] = []
                    self.streams[c_id].append(s)

            # 5. Load Logos
            print(" - Fetching Logos...")
            logo_res = requests.get(f"{self.base_url}/logos.json")
            all_logos = logo_res.json()
            
            # Map logos to channels
            # Some channels have multiple logos; we'll just pick the first one we find for now,
            # or maybe prioritize by width if needed.
            for l in all_logos:
                c_id = l.get('channel')
                if c_id and c_id in self.channels:
                    # Only assign if not already assigned, or overwrite if needed.
                    # Simple strategy: first one wins.
                    if 'logo' not in self.channels[c_id]:
                        self.channels[c_id]['logo'] = l.get('url')

            self.data_loaded = True
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Data load complete.")
            print(f"   Stats: {len(self.channels)} channels, {len(all_streams)} streams, {len(self.countries)} countries, {len(all_logos)} logos processed.")

        except Exception as e:
            print(f"Error loading data: {e}")

    def get_channels_by_filter(self, country_code=None, category_id=None, search_query=None):
        results = []
        
        # Optimization: If no filters, return top 100 or something to avoid crashing browser?
        # Better: Required at least one filter or return paginated/limited list.
        # For now, we iterate all.
        
        query = search_query.lower() if search_query else None

        for c_id, channel in self.channels.items():
            # Filter by Country
            if country_code and channel.get('country') != country_code:
                continue
            
            # Filter by Category
            if category_id and category_id not in channel.get('categories', []):
                continue
            
            # Filter by Search
            if query:
                c_name = channel.get('name', '').lower()
                match = query in c_name
                # Also check stream titles if we have them (expensive loop inside loop, maybe skip for now or optimize)
                if not match and c_id in self.streams:
                     for s in self.streams[c_id]:
                         if s.get('title') and query in s.get('title').lower():
                             match = True
                             break
                if not match:
                    continue

            # Only include channels that have streams
            if c_id in self.streams:
                results.append(channel)
        
        # Sort by name
        results.sort(key=lambda x: x.get('name', ''))
        return results

    def get_channel_details(self, channel_id):
        channel = self.channels.get(channel_id)
        if not channel:
            return None
        
        streams = self.streams.get(channel_id, [])
        
        # Enrich with country and category names
        country_obj = self.countries.get(channel.get('country'))
        country_name = country_obj.get('name') if country_obj else channel.get('country')
        
        category_names = []
        for cat_id in channel.get('categories', []):
            cat_obj = self.categories.get(cat_id)
            if cat_obj:
                category_names.append(cat_obj['name'])
        
        return {
            'info': channel,
            'streams': streams,
            'country_name': country_name,
            'category_names': category_names
        }

# Initialize and load data on startup
iptv = IPTVManager()
# We can load data now or on first request. Loading now ensures it's ready.
# Note: In a production server (gunicorn), this would run on every worker boot.
iptv.load_data()

@app.route('/')
def index():
    # Dashboard view
    total_channels = len(iptv.channels)
    total_countries = len(iptv.countries)
    total_streams = sum(len(s) for s in iptv.streams.values())
    
    # Get some featured/random channels (e.g., top US News channels for now as a default)
    featured = iptv.get_channels_by_filter(country_code='US', category_id='news')[:8]
    
    return render_template('index.html', 
                           total_channels=total_channels,
                           total_countries=total_countries,
                           total_streams=total_streams,
                           featured=featured)

@app.route('/browse')
def browse():
    country = request.args.get('country')
    category = request.args.get('category')
    search = request.args.get('search')
    
    # If no filters provided, default to US to avoid showing 10k channels
    if not country and not category and not search:
        country = 'US'
        
    channels = iptv.get_channels_by_filter(country_code=country, category_id=category, search_query=search)
    
    # Pagination (Basic)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_channels = channels[start:end]
    has_next = len(channels) > end
    
    # Metadata for display
    selected_country_name = iptv.countries.get(country, {}).get('name') if country else "All Countries"
    selected_category_name = iptv.categories.get(category, {}).get('name') if category else "All Categories"

    return render_template('browse.html', 
                           channels=paginated_channels,
                           page=page,
                           has_next=has_next,
                           country=country,
                           category=category,
                           search=search,
                           selected_country_name=selected_country_name,
                           selected_category_name=selected_category_name)

@app.route('/countries')
def countries():
    # Return list of countries that actually have channels
    # Filter countries to those that exist in our channel list
    active_country_codes = set()
    for c in iptv.channels.values():
        if c.get('country'):
            active_country_codes.add(c['country'])
            
    active_countries = []
    for code, c_obj in iptv.countries.items():
        if code in active_country_codes:
            active_countries.append(c_obj)
            
    active_countries.sort(key=lambda x: x['name'])
    return render_template('countries.html', countries=active_countries)

@app.route('/categories')
def categories():
    cats = list(iptv.categories.values())
    cats.sort(key=lambda x: x['name'])
    return render_template('categories.html', categories=cats)

@app.route('/channel/<channel_id>')
def channel_detail(channel_id):
    data = iptv.get_channel_details(channel_id)
    if not data:
        abort(404)
    return render_template('channel.html', **data)

@app.route('/watch')
def watch():
    url = request.args.get('url')
    title = request.args.get('title')
    if not url:
        return redirect(url_for('index'))
    return render_template('watch.html', url=url, title=title)

if __name__ == '__main__':
    app.run(debug=True, port=5000)