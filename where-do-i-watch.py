import streamlit as st
from tmdbv3api import TMDb, Movie, TV, Search
from tmdbv3api.exceptions import TMDbException

# --- Configuration ---
# IMPORTANT: Paste your API key between the quotes below.
api_key = st.secrets["MY_API_KEY"]


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

def get_recommendations(media_id, media_type):
    """Fetches recommendations based on the selected title."""
    try:
        engine = Movie() if media_type == 'movie' else TV()
        return engine.recommendations(media_id)
    except Exception as e:
        st.warning(f"Could not fetch recommendations: {e}")
        st.warning(f"Could not fetch recommendations: {e}")
        return []

def process_search(query, country_code):
    """Refactored search processing function."""
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
                                for provider in country_providers[i][provider_type]:
                                    if provider['provider_id'] not in seen_providers:
                                        provider_list.append({
                                            "name": provider['provider_name'],
                                            "logo_url": f"https://image.tmdb.org/t/p/w92{provider['logo_path']}"
                                        })
                                        seen_providers.add(provider['provider_id'])
                                        
                    results_dict['providers'] = provider_list
                    
                # Parse Top 4 Recommendations
                recs_data = get_recommendations(first_result.id, first_result.media_type)
                results_dict["recommendations"] = []
                
                # Convert to list to handle AsObj which doesn't support slicing
                recs_list = list(recs_data) if recs_data else []
                for r in recs_list[:4]:
                    results_dict["recommendations"].append({
                        "title": getattr(r, 'title', getattr(r, 'name', 'Unknown')),
                        "poster": f"https://image.tmdb.org/t/p/w300{r.poster_path}" if r.poster_path else 'https://placehold.co/300x450',
                        "summary": getattr(r, 'overview', 'No summary available.')
                    })

        # Store results in session state to persist them across reruns
        st.session_state.results = results_dict

    except TMDbException as e:
        st.error(f"TMDb API Error: {e}. This might be due to an invalid API key or a network issue.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# --- Streamlit App Layout ---

st.set_page_config(page_title="Where Do I Watch", layout="centered")

st.title("🎬 Where Do I Watch")
# st.markdown("Find out where to watch your favorite movies and TV shows.")

# --- API Key Input Section ---
# Use session_state to store the API key
st.session_state.api_key = api_key


if 'api_key' not in st.session_state or not st.session_state.api_key:
    st.header("Enter your TMDB API Key")
    st.markdown("You can get a free API key from [The Movie Database (TMDb)](https://www.themoviedb.org/signup).")
    
    api_key_input = st.text_input("TMDB API Key", type="password")
    
    if st.button("Save API Key"):
        if api_key_input:
            st.session_state.api_key = api_key_input

            st.success("API Key saved! The app will now load.")
            st.rerun()


        else:
            st.warning("Please enter a valid API key.")
else:
    # --- Main Application (if API key is present) ---
    st.markdown("Find out where to watch your favorite movies and TV shows.")

    tmdb = TMDb()
    tmdb.api_key =  st.session_state.api_key
    tmdb.language = 'en'
    tmdb.debug = False


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
            process_search(query, SUPPORTED_COUNTRIES[selected_country_name])

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
            
            # Display provider logos in a grid
            cols = st.columns(4) 
            for i, provider in enumerate(results['providers']):
                with cols[i % 4]:
                    st.image(provider['logo_url'], width=75)
                    st.caption(provider['name'])
        
        
            # for provider_type, provider_list in results['providers'].items():
            #     st.markdown(f"**{provider_type}**")
            #     cols = st.columns(5) 
            #     for i, provider in enumerate(provider_list):
            #         with cols[i % 5]:
            #             st.image(provider['logo_url'], width=60)
            #             st.caption(provider['name'])
            #     st.markdown("<br>", unsafe_allow_html=True)
            
            if results['justwatch_url']:
                st.markdown(f"[See more options on JustWatch]({results['justwatch_url']})", unsafe_allow_html=True)
        else:
            st.warning(f"No streaming providers found for this title in {results['country_name']}.")

        # Recommendations
        if results.get('recommendations'):
            st.divider()
            st.subheader("🎬 You might also like")
            r_cols = st.columns(4)
            for i, rec in enumerate(results['recommendations']):
                with r_cols[i]:
                    st.image(rec['poster'], use_container_width=True)
                    if st.button(f"Where Do I Watch", key=f"rec_{i}_{rec['title']}"):
                        process_search(rec['title'], results['country_name'])
                        st.rerun()
                    with st.expander("Summary"):
                        st.caption(rec['summary'])