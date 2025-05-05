import webview
from app import app

if __name__ == '__main__':
    # Start Flask in a thread-safe way
    import threading

    def run_flask():
        app.run(debug=False, port=5000, threaded=True)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait a short time to ensure the server starts before opening WebView
    import time
    time.sleep(1)

    # Open WebView window pointing to the Flask app
    webview.create_window("Design Record Manager", "http://127.0.0.1:5000", width=1200, height=800)
    webview.start()
