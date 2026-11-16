"""
upload_algorithm_short.py
Uploads escape_view_jails_2026_short.mp4 to YouTube channel Ishowheattt
with optimized title, description, tags, category, and thumbnail.
"""

import os
import sys
from youtube_uploader import YouTubeUploader

def main():
    video_path = os.path.abspath("clips/escape_view_jails_2026_short.mp4")
    thumb_path = os.path.abspath("clips/escape_view_jails_thumb.jpg")

    if not os.path.exists(video_path):
        print(f"[!] Video file not found: {video_path}")
        sys.exit(1)

    title = "Why Your Shorts Get Stuck at 200 Views 🚨"
    
    description = (
        "Why do your YouTube Shorts abruptly stop getting views at 200 or 1,000? "
        "In this 2026 algorithm breakdown, we explain how YouTube tests your hook in the first 2 seconds, "
        "why 30% swipe-away kills impressions, and how to escape the view jails.\n\n"
        "⚠️ Rated 18% Spicy | Unfiltered creator truth & harsh algorithm realities. Viewer discretion advised.\n\n"
        "TIMESTAMPS:\n"
        "0:00 - The 200-View Trap\n"
        "0:08 - The 2-Second Swipe Test\n"
        "0:16 - Escaping the 1K Ceiling\n"
        "0:22 - The Infinite Loop Fix\n\n"
        "#Shorts #YouTubeAlgorithm #CreatorTips #AlgorithmHacks #Gaming"
    )

    tags = ["shorts", "youtube algorithm", "view jail", "creator tips", "algorithm hacks", "gaming"]

    print("=" * 65)
    print("  🚀  UPLOADING 2026 ALGORITHM SHORT TO YOUTUBE")
    print("=" * 65)
    print(f"Video:       {os.path.basename(video_path)}")
    print(f"Title:       {title}")
    print(f"Thumbnail:   {os.path.basename(thumb_path) if os.path.exists(thumb_path) else 'None'}")
    print(f"Privacy:     public")
    print(f"Category:    27 (Education / Creator Intel)")
    print("-" * 65)

    uploader = YouTubeUploader()
    if not uploader.authenticate():
        print("[!] Failed to authenticate with YouTube API.")
        sys.exit(1)

    ch = uploader.get_channel_info()
    if ch:
        print(f"[✔] Channel Target: {ch['title']} (ID: {ch['id']}) | Subs: {ch['subs']}")

    res = uploader.upload_short(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
        privacy_status="public",
        category_id="27"
    )

    if res.get("success"):
        video_id = res["video_id"]
        print("\n" + "=" * 65)
        print("  🎉  UPLOAD SUCCESSFUL!")
        print("=" * 65)
        print(f"Video ID:    {video_id}")
        print(f"Shorts URL:  https://youtube.com/shorts/{video_id}")
        print(f"Watch URL:   https://www.youtube.com/watch?v={video_id}")
        print("=" * 65)
    else:
        print(f"\n[!] Upload failed: {res.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
