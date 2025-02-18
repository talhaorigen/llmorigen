
import http.server
import socketserver
import yaml
import os
import mimetypes
from pyprojroot import here

# Load configuration
with open(here("configs/app_config.yml")) as cfg:
    app_config = yaml.load(cfg, Loader=yaml.FullLoader)

PORT = app_config["serve"]["port"]
DIRECTORY1 = os.path.abspath(app_config["directories"]["data_directory"])
DIRECTORY2 = os.path.abspath(app_config["directories"]["data_directory_2"])
CUSTOM_DIRECTORY = os.path.abspath(app_config["directories"]["custom_persist_directory"])

# Ensure directories exist
for directory in [DIRECTORY1, DIRECTORY2, CUSTOM_DIRECTORY]:
    if not os.path.isdir(directory):
        print(f"Warning: Directory does not exist: {directory}")

class MultiDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP request handler that serves files from multiple directories.
    """

    def translate_path(self, path):
        """
        Translate a web request path into a valid file system path.
        """
        path = path.lstrip("/")  # Remove leading slash
        parts = path.split('/', 1)
        first_directory = parts[0]

        # If there's more than one part, reconstruct the filename
        filename = parts[1] if len(parts) > 1 else ""

        # Construct file paths for all directories
        file_path1 = os.path.join(DIRECTORY1, first_directory)
        file_path2 = os.path.join(DIRECTORY2, first_directory)
        file_path3 = os.path.join(CUSTOM_DIRECTORY, first_directory)

        print(f"🔍 Checking: {file_path1}")
        print(f"🔍 Checking: {file_path2}")
        print(f"🔍 Checking: {file_path3}")

        # Return the first valid file path
        if os.path.isfile(file_path1):
            return file_path1
        elif os.path.isfile(file_path2):
            return file_path2
        elif os.path.isfile(file_path3):
            return file_path3

        print("🚨 ERROR: File not found!")
        return super().translate_path(path)

    def end_headers(self):
        """
        Ensure correct MIME type for PDFs and other files.
        """
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow CORS
        if self.path.endswith(".pdf"):
            self.send_header("Content-Type", "application/pdf")
        else:
            file_extension = os.path.splitext(self.path)[1]
            mime_type = mimetypes.types_map.get(file_extension, "application/octet-stream")
            self.send_header("Content-Type", mime_type)

        super().end_headers()

    def do_GET(self):
        """
        Handle GET requests and log errors properly.
        """
        requested_file = self.translate_path(self.path)

        if not os.path.isfile(requested_file):
            print("🚨 ERROR: File not found!")
            self.send_error(404, "File Not Found")
            return

        print(f"✅ Serving File: {requested_file}")
        super().do_GET()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MultiDirectoryHTTPRequestHandler) as httpd:
        print(f"🚀 Serving at http://localhost:{PORT}")
        httpd.serve_forever()
