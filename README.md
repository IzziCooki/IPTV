# Open IPTV Browser

This project provides both a command-line interface (CLI) and a web-based user interface to browse and watch free, public IPTV streams from around the world, utilizing data from the [iptv-org/api](https://github.com/iptv-org/api) project.

## Features

### Web UI (`app.py`)

A full-fledged web application built with Flask, offering a rich user experience for browsing and watching IPTV streams.

*   **Dashboard**: Overview of available channels, countries, and streams.
*   **Global Browse**: Explore channels by Country or Category.
*   **Search**: Powerful search functionality to find channels by name or stream title across all available data.
*   **Detailed Channel View**: Access information about specific channels, including their logo, country, network, website, and available streams.
*   **Integrated Video Player**: Watch HLS (`.m3u8`) streams directly in your browser using [HLS.js](https://github.com/video-dev/hls.js).
*   **Responsive Design**: Built with Bootstrap 5, providing a modern and mobile-friendly interface with a dark theme.
*   **Logo Display**: Channel logos are correctly fetched and displayed.

### CLI (`main.py`)

A simple command-line tool for quick access to IPTV stream information.

*   **Browse by Category**: Select a category and then search for channels within it.
*   **Global Search**: Search for channels by name or stream title across all categories.
*   **Stream Details**: Displays channel name, stream title, URL, and quality.

## Setup

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/IPTV.git # Replace with your repo URL
    cd IPTV
    ```

2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (The `requirements.txt` file needs to be created or updated if not present with `flask`, `requests`.)

## How to Run

### Web UI (Flask Application)

The web UI provides a graphical interface in your browser.

1.  **Activate your virtual environment** (if not already active).
2.  **Run the Flask application:**
    ```bash
    ./venv/bin/python app.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5000`.

    *Note: The first time you run `app.py`, it will fetch a large amount of data from the `iptv-org` API (channels, streams, logos, countries, categories). This might take a few moments depending on your internet connection. Subsequent runs will also fetch the latest data.*

### CLI Application

The CLI application allows you to interact with the IPTV data directly from your terminal.

1.  **Activate your virtual environment** (if not already active).
2.  **Run the CLI application:**
    ```bash
    ./venv/bin/python main.py
    ```
3.  Follow the on-screen prompts to browse or search for streams.

    *Note: Similar to the web UI, the CLI will fetch data from the `iptv-org` API on startup, which may take some time.*

## API Data Source

This project relies on the excellent data provided by the [iptv-org](https://github.com/iptv-org) community.
*   **API Endpoints**: [iptv-org/api](https://github.com/iptv-org/api)
*   **Database**: [iptv-org/database](https://github.com/iptv-org/database)

The data includes a comprehensive list of channels, streams, logos, countries, and categories, enabling a rich browsing experience.
