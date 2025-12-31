import requests

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
            channel_id = s.get('channel')
            channel_info = self.channels.get(channel_id, {})
            channel_name = channel_info.get('name', '').lower()
            stream_title = s.get('title', '').lower()

            if query in channel_name or query in stream_title:
                display_title = channel_info.get('name', 'Unknown Channel')
                if s.get('title') and s.get('title').lower() != display_title.lower():
                    display_title += f" - {s.get('title')}"

                results.append({
                    'title': display_title,
                    'url': s.get('url'),
                    'quality': s.get('height', 'N/A')
                })
        
        return results

    def display_results(self, results):
        if not results:
            print("\nNo streams found matching that criteria.")
            return

        print(f"\nFound {len(results)} results:")
        print("-" * 80)
        for i, res in enumerate(results[:20], 1): # Limit to top 20 for readability
            print(f"{i}. {res['title']} ({res['quality']})")
            print(f"   URL: {res['url']}")
        
        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more results.")
        print("-" * 80)

def main():
    iptv = IPTVManager()
    iptv.load_data()
    
    available_categories = iptv.get_categories()

    while True:
        print("\nIPTV Stream Search - US Channels")
        print("1. Select a Category to browse")
        print("2. Search all channels")
        print("3. Exit")
        
        choice = input("\nSelect an option: ")

        if choice == '1':
            print("\nAvailable Categories:")
            for i, cat in enumerate(available_categories, 1):
                print(f"{i}. {cat}")
            
            try:
                cat_choice_num = int(input("\nSelect a category number: "))
                if 1 <= cat_choice_num <= len(available_categories):
                    selected_category = available_categories[cat_choice_num - 1]
                    
                    while True:
                        print(f"\n-- Browsing Category: {selected_category} --")
                        query = input("Enter search term (or leave blank to see all, type 'back' to return): ")

                        if query.lower() == 'back':
                            break
                        
                        results = iptv.search(query, category=selected_category)
                        iptv.display_results(results)
                else:
                    print("Invalid category number.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == '2':
            query = input("Enter search term: ")
            results = iptv.search(query)
            iptv.display_results(results)

        elif choice == '3':
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()