"""
YouTube Shorts Auto-Uploader & Publisher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connects to YouTube Data API v3 via OAuth 2.0.
Uploads vertical shorts, applies SEO metadata, tags, and custom high-CTR thumbnails.
Adapted from Moh-Tayyab/youtube-automation.
"""

import os
import sys
import json
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_PATH = os.path.join(DIR, "client_secrets.json")
CREDENTIALS_PATH = os.path.join(DIR, "youtube_credentials.json")

# Scopes needed for uploading and setting thumbnail
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]


class YouTubeUploader:
    def __init__(self, secrets_file: str = CLIENT_SECRETS_PATH, creds_file: str = CREDENTIALS_PATH):
        self.secrets_file = secrets_file
        self.creds_file = creds_file
        self.youtube = None

    def authenticate(self) -> bool:
        """Authenticates using cached tokens or initiates local OAuth browser flow."""
        # 1. Try loading existing valid tokens
        if os.path.exists(self.creds_file):
            try:
                creds = Credentials.from_authorized_user_file(self.creds_file, SCOPES)
                if creds and creds.valid:
                    self.youtube = build("youtube", "v3", credentials=creds)
                    print("[✔] Authenticated successfully from saved session.")
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    self.youtube = build("youtube", "v3", credentials=creds)
                    with open(self.creds_file, "w") as f:
                        f.write(creds.to_json())
                    print("[✔] Token refreshed successfully.")
                    return True
            except Exception as e:
                print(f"[!] Session token expired/invalid: {e}")

        # 2. Check if client_secrets.json or any client_secret*.json exists
        if not os.path.exists(self.secrets_file):
            import glob
            matches = glob.glob(os.path.join(DIR, "client_secret*.json"))
            if matches:
                self.secrets_file = matches[0]
                print(f"[*] Detected OAuth secret file: {os.path.basename(self.secrets_file)}")
            else:
                print("\n" + "=" * 65)
                print("❌ MISSING 'client_secrets.json'")
                print("=" * 65)
                print("To connect your YouTube channel, follow these 3 quick steps:")
                print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
                print("2. Enable 'YouTube Data API v3' in APIs & Services.")
                print("3. Create an 'OAuth Client ID' (Desktop App), click 'Download JSON',")
                print(f"   and save it as: {self.secrets_file}")
                print("=" * 65 + "\n")
                return False

        # 3. Run OAuth web flow on local port 8080
        print("[*] Launching browser to authorize your YouTube channel...")
        flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        self.youtube = build("youtube", "v3", credentials=creds)

        with open(self.creds_file, "w") as f:
            f.write(creds.to_json())
        print(f"[✔] Credentials saved to: {self.creds_file}")
        return True

    def get_channel_info(self) -> dict | None:
        """Fetches channel title, subscribers, and details."""
        if not self.youtube:
            return None
        try:
            resp = self.youtube.channels().list(part="snippet,statistics", mine=True).execute()
            if resp.get("items"):
                ch = resp["items"][0]
                return {
                    "title": ch["snippet"]["title"],
                    "id": ch["id"],
                    "subs": ch["statistics"].get("subscriberCount", "N/A"),
                    "videos": ch["statistics"].get("videoCount", "N/A")
                }
        except Exception as e:
            print(f"[!] Failed to get channel info: {e}")
        return None

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        thumbnail_path: str | None = None,
        privacy_status: str = "public",
        category_id: str = "20"  # 20 = Gaming
    ) -> dict:
        """
        Uploads a video to YouTube with Shorts formatting and sets the custom thumbnail.
        """
        if not self.youtube:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video not found: {video_path}"}

        # Format title with #Shorts hashtag if not present
        if "#shorts" not in title.lower():
            title = f"{title} #Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags or ["shorts", "gaming", "clips"],
                "categoryId": category_id,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        print(f"[*] Uploading to YouTube: '{title}' (Privacy: {privacy_status})...")
        media = MediaFileUpload(video_path, chunksize=1024 * 1024 * 4, resumable=True)
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[⏳] Upload Progress: {int(status.progress() * 100)}%")

        if response and "id" in response:
            video_id = response["id"]
            video_url = f"https://youtube.com/shorts/{video_id}"
            print(f"🎉 [SUCCESS] Uploaded live to YouTube Shorts: {video_url}")

            # Upload custom thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    print(f"[*] Uploading custom thumbnail: {thumbnail_path}...")
                    self.youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                    print("[✔] Thumbnail set successfully!")
                except Exception as e:
                    print(f"[!] Thumbnail upload warning (requires verified channel): {e}")

            return {
                "success": True,
                "video_id": video_id,
                "url": video_url,
                "title": title
            }

        return {"success": False, "error": "No video ID returned by YouTube API"}


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Auto-Uploader")
    parser.add_argument("--auth", action="store_true", help="Run initial OAuth login")
    parser.add_argument("--video", help="Path to video file (.mp4)")
    parser.add_argument("--thumbnail", help="Path to thumbnail image (.jpg)")
    parser.add_argument("--title", help="Video Title")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"], help="Privacy status")
    parser.add_argument("--streamer", default="Streamer", help="Streamer name for SEO")
    args = parser.parse_args()

    uploader = YouTubeUploader()

    if args.auth:
        if uploader.authenticate():
            ch = uploader.get_channel_info()
            if ch:
                print(f"\n[✔] Connected Channel: {ch['title']} ({ch['subs']} subscribers, {ch['videos']} videos)")
        return

    if args.video:
        import viral_hook_engine
        title = args.title or viral_hook_engine.generate_clickbait_title(args.streamer)
        meta = viral_hook_engine.generate_seo_metadata(args.streamer, title)

        res = uploader.upload_short(
            video_path=args.video,
            title=meta["title"],
            description=meta["description"],
            tags=meta["tags"],
            thumbnail_path=args.thumbnail,
            privacy_status=args.privacy
        )
        if not res["success"]:
            print(f"[!] Upload failed: {res.get('error')}")


if __name__ == "__main__":
    main()
