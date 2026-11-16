"""
YouTube Channel Bio & Branding Optimizer
Updates Ishowheattt's channel description, keywords, and settings via YouTube Data API v3.
"""

import json
from youtube_uploader import YouTubeUploader

CHANNEL_ID = "UCmo8HUJy6OnDG0bUTsoPXLw"

BIO_TEXT = (
    "The ultimate hub for unhinged stream moments, 0.001s reactions, GTA 6 hype, and daily gaming highlights. ⚡\n\n"
    "Featuring Speed moments, chaotic stream breakdowns, and hilarious gaming reactions. Rated 18% spicy for indirect humor & mature jokes. 🌶️\n\n"
    "🔔 Subscribe for daily stream moments transformed with dynamic edits, kinetic subtitles, and custom sound design under Fair Use."
)

KEYWORDS = (
    'Ishowheattt "IShowSpeed" "IShowSpeed clips" "GTA 6" "gaming shorts" '
    '"stream moments" "funny gaming" "speed reactions" "viral gaming clips"'
)


def update_channel():
    uploader = YouTubeUploader()
    if not uploader.authenticate():
        print("[!] Authentication failed.")
        return False

    body = {
        "id": CHANNEL_ID,
        "brandingSettings": {
            "channel": {
                "description": BIO_TEXT,
                "keywords": KEYWORDS,
                "defaultLanguage": "en",
                "country": "IN"
            }
        }
    }

    try:
        res = uploader.youtube.channels().update(part="brandingSettings", body=body).execute()
        print("[✔] Channel bio & branding updated successfully!")
        desc = res.get("brandingSettings", {}).get("channel", {}).get("description", "")
        kw = res.get("brandingSettings", {}).get("channel", {}).get("keywords", "")
        print(f"[*] New Bio: {desc[:100]}...")
        print(f"[*] New Keywords: {kw}")
        return True
    except Exception as e:
        print(f"[!] Channel update error: {e}")
        return False


if __name__ == "__main__":
    update_channel()
