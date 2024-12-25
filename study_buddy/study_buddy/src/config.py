import tempfile

# Temporary directory for uploaded files
UPLOAD_DIR = tempfile.TemporaryDirectory()

# Cache size for storing recent results
CACHE_SIZE = 5
processed_cache = {}

