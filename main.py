import requests

class IPTVManager:
    def __init__(self):
        self.base_url = "https://iptv-org.github.io/api"
        self.streams = []
        self.channels = {}
        self.categories = {}
        self.countries = {}

    def load_data(self):
        """Fetches all necessary data from the API (Global)."""
        print("Fetching latest data from global API... (this may take a moment)")
        try:
            # Fetch all available categories
            category_res = requests.get(f"{self.base_url}/categories.json")
            self.categories = {cat['id']: cat['name'] for cat in category_res.json()}

            # Fetch all countries
            country_res = requests.get(f"{self.base_url}/countries.json")
            self.countries = {c['code']: c['name'] for c in country_res.json()}

            # Fetch all channels
            channel_res = requests.get(f"{self.base_url}/channels.json")
            all_channels = channel_res.json()
            # Index channels by ID
            self.channels = {c['id']: c for c in all_channels}

            # Fetch all streams
            stream_res = requests.get(f"{self.base_url}/streams.json")
            all_streams = stream_res.json()

            # Filter streams to only include those that have valid channels
            # Note: We are NO LONGER filtering just for US.
            self.streams = [s for s in all_streams if s.get('channel') in self.channels]
            
            print(f"Loaded {len(self.streams)} streams from {len(self.channels)} global channels.\n")

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

    def get_active_countries(self):
        """Returns a sorted list of countries (code, name) that have channels."""
        active_codes = set()
        for channel in self.channels.values():
            if channel.get('country'):
                active_codes.add(channel['country'])
        
        result = []
        for code in active_codes:
            name = self.countries.get(code, code)
            result.append({'code': code, 'name': name})
        
        # Sort by name
        result.sort(key=lambda x: x['name'])
        return result

    def search(self, query, category=None, country_code=None):
        """Searches streams by title, optionally filtering by category or country."""
        query = query.lower()
        results = []

        # First, filter by category/country
        streams_to_search = []
        
        cat_id_to_find = None
        if category:
            for cid, cname in self.categories.items():
                if cname.lower() == category.lower():
                    cat_id_to_find = cid
                    break

        for s in self.streams:
            channel_info = self.channels.get(s.get('channel'), {})
            
            # Filter by Category
            if cat_id_to_find and cat_id_to_find not in channel_info.get('categories', []):
                continue
            
            # Filter by Country
            if country_code and channel_info.get('country') != country_code:
                continue
                
            streams_to_search.append(s)


        # Then, search by title within the filtered list
        for s in streams_to_search:
            # If query is empty, return all matches for filters
            channel_id = s.get('channel')
            channel_info = self.channels.get(channel_id, {})
            channel_name = channel_info.get('name', '').lower()
            stream_title = s.get('title', '').lower()

            if not query or (query in channel_name or query in stream_title):
                display_title = channel_info.get('name', 'Unknown Channel')
                if s.get('title') and s.get('title').lower() != display_title.lower():
                    display_title += f" - {s.get('title')}"

                results.append({
                    'title': display_title,
                    'url': s.get('url'),
                    'quality': s.get('height', 'N/A'),
                    'country': channel_info.get('country')
                })
        
        return results

    def display_results(self, results):
        if not results:
            print("\nNo streams found matching that criteria.")
            return

        print(f"\nFound {len(results)} results:")
        print("-" * 80)
        for i, res in enumerate(results[:20], 1): # Limit to top 20 for readability
            print(f"{i}. {res['title']} ({res['country']}) - {res['quality']}")
            print(f"   URL: {res['url']}")
        
        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more results.")
        print("-" * 80)

def main():
    iptv = IPTVManager()
    iptv.load_data()
    
    available_categories = iptv.get_categories()

    while True:
        print("\nIPTV Stream Search - Global")
        print("1. Select a Category to browse")
        print("2. Search by Country")
        print("3. Search all channels")
        print("4. Exit")
        
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
            active_countries = iptv.get_active_countries()
            print("\nAvailable Countries:")
            # Too many to list all? Maybe list regions or top 50, or just list all.
            # Let's list all in columns or just list. There are ~200.
            # For CLI usability, maybe ask for search term first?
            # "Enter country code or name search:"
            
            c_query = input("Enter country name or code to filter list (leave blank for all): ").lower()
            filtered_countries = [c for c in active_countries if c_query in c['name'].lower() or c_query in c['code'].lower()]
            
            for i, c in enumerate(filtered_countries, 1):
                print(f"{i}. {c['name']} ({c['code']})")
                
            if not filtered_countries:
                print("No countries found.")
                continue

            try:
                c_choice_num = int(input("\nSelect a country number: "))
                if 1 <= c_choice_num <= len(filtered_countries):
                    selected_country = filtered_countries[c_choice_num - 1]
                    print(f"\nSelected: {selected_country['name']}")
                    
                    while True:
                        print(f"\n-- Browsing Country: {selected_country['name']} --")
                        query = input("Enter search term (or leave blank to see all, type 'back' to return): ")

                        if query.lower() == 'back':
                            break
                        
                        results = iptv.search(query, country_code=selected_country['code'])
                        iptv.display_results(results)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")


        elif choice == '3':
            query = input("Enter search term: ")
            results = iptv.search(query)
            iptv.display_results(results)

        elif choice == '4':
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
