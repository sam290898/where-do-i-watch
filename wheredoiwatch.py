# --- Setup Instructions ---
# 1. Make sure you have Python installed.
# 2. Install the required libraries by running this command in your terminal:
#    pip install streamlit tmdbv3api
# 3. Get a free API key from The Movie Database (TMDb).
#    - Create an account at https://www.themoviedb.org/
#    - Go to your account settings -> API section and generate a key.
# 4. Paste your API key into the API_KEY variable below.
# 5. Save this file (e.g., as streamlit_app.py).
# 6. Run the app from your terminal: streamlit run streamlit_app.py

import streamlit as st
from tmdbv3api import TMDb, Movie, TV, Search
from tmdbv3api.exceptions import TMDbException

# --- Configuration ---
# IMPORTANT: Paste your API key between the quotes below.
API_KEY = '3baf6f00e9596f6c8a8657d20cd48c3d'

# Initialize TMDb API
tmdb = TMDb()
tmdb.api_key = API_KEY
tmdb.language = 'en'
tmdb.debug = False

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

def get_watch_providers(media_id, media_type):
    """Fetches watch providers for a given media ID and type."""
    try:
        if media_type == 'movie':
            return Movie().watch_providers(media_id)
        elif media_type == 'tv':
            return TV().watch_providers(media_id)
    except TMDbException as e:
        st.error(f"Error fetching provider data from TMDb: {e}")
    return None

# --- Streamlit App Layout ---

st.set_page_config(page_title="Streaming Finder", layout="centered")

st.title("🎬 Streaming Service Finder")
st.markdown("Find out where to watch your favorite movies and TV shows.")

# Check for API Key
# if API_KEY == '3baf6f00e9596f6c8a8657d20cd48c3d':
#     st.error("Please add your TMDB API key to the `streamlit_app.py` script.")
#     st.stop()

# Use a form to group inputs and prevent re-running on every interaction
with st.form(key='search_form'):
    query = st.text_input("Enter a movie or TV show name")
    
    # Get country names for the selectbox
    country_names = list(SUPPORTED_COUNTRIES.keys())
    selected_country_name = st.selectbox("Choose a country", options=country_names, index=country_names.index("United States"))
    
    submit_button = st.form_submit_button(label='Search')

if submit_button:
    if not query:
        st.warning("Please enter a movie or TV show name.")
    else:
        try:
            # Clear previous results
            if 'results' in st.session_state:
                del st.session_state.results

            with st.spinner(f"Searching for '{query}'..."):
                search = Search()
                search_results = search.multi(query)

                if not search_results:
                    st.error(f"No results found for '{query}'. Please try another title.")
                else:
                    first_result = search_results[0]
                    providers_data = get_watch_providers(first_result.id, first_result.media_type)
                    country_code = SUPPORTED_COUNTRIES[selected_country_name]

                    # Structure the results to be stored in session state
                    results_dict = {
                                    "title": getattr(first_result, 'title', getattr(first_result, 'name', 'Unknown Title')),
                                    "overview": getattr(first_result, 'overview', 'No overview available.'),
                                    "poster_url": f"https://image.tmdb.org/t/p/w200{first_result.poster_path}" if first_result.poster_path else 'https://placehold.co/200x300/111827/FFFFFF?text=No+Image',
                                    "providers": [],
                                    "justwatch_url": "",
                                    "country_name": country_code
                                }
                    indx = 0
                    for idx, name  in enumerate(providers_data['results']):
                        if country_code == str(name['results']):
                            indx = idx
                    
                    pp = dict(providers_data['results'][indx])
                    
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

            # Store results in session state to persist them across reruns
            st.session_state.results = results_dict

        except TMDbException as e:
            st.error(f"TMDb API Error: {e}. This might be due to an invalid API key or a network issue.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Display results if they exist in the session state
if 'results' in st.session_state:
    results = st.session_state.results
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(results['poster_url'], use_container_width=True)

    with col2:
        st.header(results['title'])
        st.caption(results['overview'])

    st.markdown("---")

    if results['providers']:
        st.subheader(f"Available in {results['country_name']}:")
        
    #     # Display provider logos in a grid
    #     cols = st.columns(4) 
    #     for i, provider in enumerate(results['providers']):
    #         with cols[i % 4]:
    #             st.image(provider['logo_url'], width=75)
    #             st.caption(provider['name'])
    
    
        for provider_type, provider_list in results['providers'].items():
            st.markdown(f"**{provider_type}**")
            cols = st.columns(5) 
            for i, provider in enumerate(provider_list):
                with cols[i % 5]:
                    st.image(provider['logo_url'], width=60)
                    st.caption(provider['name'])
            st.markdown("<br>", unsafe_allow_html=True)
        
        if results['justwatch_url']:
            st.markdown(f"[See more options on JustWatch]({results['justwatch_url']})", unsafe_allow_html=True)
    else:
        st.warning(f"No streaming providers found for this title in {results['country_name']}.")

st.markdown("---")
st.markdown("Powered by <a href='https://www.themoviedb.org/' target='_blank'>TMDb</a>", unsafe_allow_html=True)
