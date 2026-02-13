# 🎬 Where Do I Watch

**Where Do I Watch** is a Streamlit-based web application that helps you find where to stream, rent, or buy your favorite movies and TV shows in your country. It uses the TMDb API to fetch real-time streaming availability and provides personalized recommendations.

## ✨ Features

- **Global Search**: Search for any movie or TV show.
- **Country-Specific Availability**: Check streaming services (Netflix, Amazon Prime, Disney+, etc.), rental options, and purchase options for over 40 countries.
- **Interactive Recommendations**: Discover similar content with the "You might also like" section. Click on any recommendation to instantly see where to watch it!
- **Direct JustWatch Links**: Get a direct link to JustWatch for even more viewing options.
- **Responsive UI**: Clean and user-friendly interface powered by Streamlit.

## 🛠️ Technologies Used

- **Python 3**: Core programming language.
- **Streamlit**: For building the interactive web application.
- **TMDb API (via `tmdbv3api`)**: For fetching movie/TV metadata, provider info, and recommendations.

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher installed.
- A free API Key from [The Movie Database (TMDb)](https://www.themoviedb.org/signup).

### Installation

1.  **Clone the repository** (or download the files):
    ```bash
    git clone <your-repo-url>
    cd where-do-i-watch
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key**:
    You can provide your API key in two ways:
    
    *   **Option A: Secrets File (Recommended)**
        Create a file path `.streamlit/secrets.toml` in the project root and add your key:
        ```toml
        MY_API_KEY = "your_tmdb_api_key_here"
        ```
    
    *   **Option B: UI Input**
        Run the app without a secrets file, and you will be prompted to enter your API key directly in the web interface.

### Running the App

Execute the following command in your terminal:

```bash
streamlit run where-do-i-watch.py
```

The app will open in your default browser (usually at `http://localhost:8501`).

## 📂 Project Structure

- `where-do-i-watch.py`: Main application script containing all logic and UI code.
- `requirements.txt`: List of Python dependencies.
- `.streamlit/secrets.toml`: (Optional) Configuration file for storing secrets like API keys.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

[MIT License](LICENSE)
