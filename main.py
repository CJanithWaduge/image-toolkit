import webbrowser
from server import app

if __name__ == "__main__":
    print("Starting Image Toolkit...")
    print("Open http://127.0.0.1:8000 in your browser.")
    webbrowser.open("http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
