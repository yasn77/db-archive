import json

try:
    with open('version.json', 'r') as f:
        j = json.load(f)
    __version__ = j['version']
except Exception:
    __version__ = '0.0.1-unable_to_read_version_file'
