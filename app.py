# --- Setup Instructions ---
# 1. Make sure you have Python installed.
# 2. Install the Flask and tmdbv3api libraries by running this command in your terminal:
#    pip install Flask tmdbv3api
# 3. Get a free API key from The Movie Database (TMDb).
#    - Create an account at https://www.themoviedb.org/
#    - Go to your account settings -> API section and generate a key.
# 4. Paste your API key into the API_KEY variable below.
# 5. Run this script from your terminal: python your_script_name.py
# 6. Open your web browser and go to http://127.0.0.1:5000

import os
from flask import Flask, render_template_string, request
from tmdbv3api import TMDb, Movie, TV, Search
from tmdbv3api.exceptions import TMDbException





# --- Configuration ---
# IMPORTANT: Paste your API key between the quotes below.
API_KEY = '3baf6f00e9596f6c8a8657d20cd48c3d'

# --- App Initialization ---
# Initialize Flask App
app = Flask(__name__)

# Initialize TMDb API
tmdb = TMDb()
tmdb.api_key = API_KEY # The API key is now set directly from the variable above.
tmdb.language = 'en'
tmdb.debug = False

# --- Sanity Check on Startup ---
# This message will print in your terminal when the server starts.
print("="*60)
if tmdb.api_key and tmdb.api_key != 'YOUR_TMDB_API_KEY':
    print("✅ TMDB API key loaded successfully.")
else:
    print("❌ WARNING: TMDB API key is either missing or still the placeholder.")
    print("   Please edit the script, add your key, save the file, and restart.")
print(f"   Flask server is starting. Open http://127.0.0.1:5000 in your browser.")
print("="*60)


# Dictionary of countries and their ISO 3166-1 codes
SUPPORTED_COUNTRIES = {
    "United States": "US", "United Kingdom": "GB", "Canada": "CA",
    "Australia": "AU", "Germany": "DE", "France": "FR", "India": "IN",
    "Japan": "JP", "South Korea": "KR", "Spain": "ES", "Mexico": "MX",
    "Brazil": "BR", "Italy": "IT", "Russia": "RU", "China": "CN",
    "Argentina": "AR", "Austria": "AT", "Belgium": "BE", "Switzerland": "CH",
    "Chile": "CL", "Colombia": "CO", "Czech Republic": "CZ", "Denmark": "DK",
    "Egypt": "EG", "Finland": "FI", "Greece": "GR", "Hong Kong": "HK",
    "Hungary": "HU", "Indonesia": "ID", "Ireland": "IE", "Israel": "IL",
    "Malaysia": "MY", "Netherlands": "NL", "Norway": "NO", "New Zealand": "NZ",
    "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT",
    "Sweden": "SE", "Singapore": "SG", "Thailand": "TH", "Turkey": "TR",
    "Taiwan": "TW", "South Africa": "ZA"
}

# --- HTML Template ---
# This string contains the full HTML for our web page.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streaming Service Finder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-white">Streaming Service Finder</h1>
            <p class="text-gray-400 mt-2">Find out where to watch your favorite movies and TV shows.</p>
        </header>

        <div class="max-w-xl mx-auto bg-gray-800 p-6 rounded-lg shadow-lg">
            <form method="POST">
                <div class="flex flex-col sm:flex-row gap-4 mb-4">
                    <input type="text" name="query" class="flex-grow bg-gray-700 text-white border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter a movie or TV show..." value="{{ query or '' }}">
                    <select name="country" class="bg-gray-700 text-white border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        {% for name, code in countries.items() %}
                            <option value="{{ code }}" {% if selected_country == code %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition duration-300">Search</button>
                </div>
            </form>

            {% if error %}
                <div class="bg-red-900 border border-red-600 text-red-200 px-4 py-3 rounded-lg relative mt-6" role="alert">
                  <strong class="font-bold">Error: </strong>
                  <span class="block sm:inline">{{ error }}</span>
                </div>
            {% endif %}

            {% if results %}
                <div class="mt-6">
                    <div class="bg-gray-700 p-4 rounded-lg flex flex-col sm:flex-row items-center sm:items-start gap-4">
                        <img src="{{ results.poster_url }}" alt="{{ results.title }}" class="w-32 rounded-lg shadow-md" onerror="this.onerror=null;this.src='https://placehold.co/200x300/111827/FFFFFF?text=No+Image';">
                        <div class="text-center sm:text-left">
                            <h2 class="text-2xl font-bold">{{ results.title }}</h2>
                            <p class="text-gray-400 mt-2 text-sm">{{ results.overview }}</p>
                        </div>
                    </div>

                    {% if results.providers %}
                        <h3 class="text-xl font-semibold mt-6 mb-4 text-center">Available in {{ results.country_name }}:</h3>
                        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                            {% for provider in results.providers %}
                                <div class="flex flex-col items-center text-center">
                                    <img src="{{ provider.logo_url }}" alt="{{ provider.name }}" class="w-16 h-16 rounded-full shadow-lg mb-2">
                                    <span class="text-sm">{{ provider.name }}</span>
                                </div>
                            {% endfor %}
                        </div>
                        {% if results.justwatch_url %}
                            <div class="text-center mt-6"><a href="{{ results.justwatch_url }}" target="_blank" class="text-blue-400 hover:underline">More options on JustWatch</a></div>
                        {% endif %}
                    {% else %}
                        <p class="text-center mt-6 text-yellow-400">Not available for streaming in {{ results.country_name }}.</p>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        <footer class="text-center text-gray-500 mt-8">
            <p>Powered by <a href="https://www.themoviedb.org/" target="_blank" class="text-blue-400 hover:underline">TMDb</a></p>
        </footer>
    </div>
</body>
</html>
"""

def get_watch_providers(media_id, media_type):
    """Fetches watch providers for a given media ID and type."""
    if media_type == 'movie':
        movie = Movie()
        return movie.watch_providers(media_id)
    elif media_type == 'tv':
        tv = TV()
        return tv.watch_providers(media_id)
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route to display the page and handle form submissions."""
    # The main check is now done on startup, but we keep this as a fallback.
    # if tmdb.api_key == API_KEY or not tmdb.api_key:
    #     return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, error="Your TMDB API key is not configured in the Python script. Please add it and restart the server.")

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        country_code = request.form.get('country')
        country_name = [name for name, code in SUPPORTED_COUNTRIES.items() if code == country_code][0]

        if not query:
            return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, selected_country=country_code, error="Please enter a movie or TV show name.")

        try:
            search = Search()
            search_results = search.multi(query)

            if not search_results:
                return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, query=query, selected_country=country_code, error=f"No results found for '{query}'.")

            first_result = search_results[0]
            providers_data = get_watch_providers(first_result.id, first_result.media_type)

            results_dict = {
                "title": getattr(first_result, 'title', getattr(first_result, 'name', 'Unknown Title')),
                "overview": getattr(first_result, 'overview', 'No overview available.'),
                "poster_url": f"https://image.tmdb.org/t/p/w200{first_result.poster_path}" if first_result.poster_path else 'https://placehold.co/200x300/111827/FFFFFF?text=No+Image',
                "providers": [],
                "justwatch_url": "",
                "country_name": country_name
            }

            for idx, name  in enumerate(providers_data['results']):
                if country_code == str(name['results']):
                    index = idx
            
            pp = dict(providers_data['results'][index])
            
            if country_code in str(pp):
                country_providers = pp[country_code]
                results_dict['justwatch_url'] = country_providers[0]

                seen_providers = set()
                provider_list = []

                for provider_type in ['flatrate', 'rent', 'buy', 'ads', 'free']:
                    for i in range(1, len(country_providers)):
                        if provider_type in str(country_providers[i]):
                            print(provider_type)
                            for provider in country_providers[i][provider_type]:
                                if provider['provider_id'] not in seen_providers:
                                    provider_list.append({
                                        "name": provider['provider_name'],
                                        "logo_url": f"https://image.tmdb.org/t/p/w92{provider['logo_path']}"
                                    })
                                    seen_providers.add(provider['provider_id'])
                                    
                results_dict['providers'] = provider_list

            return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, query=query, selected_country=country_code, results=results_dict)

        except TMDbException as e:
            error_message = f"TMDb API Error: {e}. This usually means the API key is invalid or there's a problem with the request."
            return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, query=query, selected_country=country_code, error=error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, query=query, selected_country=country_code, error=error_message)

    return render_template_string(HTML_TEMPLATE, countries=SUPPORTED_COUNTRIES, selected_country='US')

if __name__ == '__main__':
    app.run(debug=True)
