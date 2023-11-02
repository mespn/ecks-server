import json

# Setting global dictionaries
with open("mime_types.json", "rb") as f:
    MIME_TYPES = json.load(f)

with open("status_codes.json", "rb") as f:
    STATUS_CODES = json.load(f)