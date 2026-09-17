import json
import os
import yt_dlp

# ---> FILL IN YOUR 6 URLS HERE <---
TARGET_URLS = [
    "https://www.youtube.com/@ReaganRenee-c2f5x",
    "https://www.youtube.com/@ReaganRenee-c2f5x/search?query=Reagan",
    "https://www.youtube.com/@LandonDavis-v7p/playlists",
    "https://www.youtube.com/@christasapp7390/featured",
]


def archive_youtube_metadata(urls):
  # Use extract_flat=False or handle playlist traversal properly
  ydl_opts = {
      "extract_flat": True,
      "skip_download": True,
  }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in urls:
      if "URL_" in url:
        print(f"Skipping placeholder URL: {url}")
        continue

      print(f"\n----------------------------------------")
      print(f"Processing URL: {url}")

      try:
        info = ydl.extract_info(url, download=False)
        if not info:
          print(f"No data found for this URL.")
          continue

        # Get the channel name for the folder structure
        channel_name = info.get(
            "uploader",
            info.get(
                "channel",
                info.get(
                    "uploader_id",
                    info.get("title", "unknown_channel"),
                ),
            ),
        )
        channel_dir = "".join(
            c for c in channel_name if c.isalnum() or c in (" ", "_", "-")
        ).strip()
        os.makedirs(channel_dir, exist_ok=True)
        print(f"Saving files to directory: ./{channel_dir}/")

        entries = info.get("entries", [])

        # Check if this URL is a channel page listing multiple playlists (like /playlists tab)
        # We can tell if the entries themselves look like playlists or have playlist IDs
        is_playlist_collection = False
        if entries:
          first_entry = entries[0]
          # If the entry has a playlist-specific URL or type indicator
          if (
              first_entry
              and "playlist" in str(first_entry.get("url", ""))
              or first_entry.get("_type") == "playlist"
          ):
            is_playlist_collection = True

        if is_playlist_collection:
          print(
              "Detected a collection of playlists. Fetching contents of each"
              " playlist..."
          )
          for entry in entries:
            if entry and "url" in entry:
              playlist_url = entry["url"]
              if not playlist_url.startswith("http"):
                playlist_url = f"https://www.youtube.com{playlist_url}"

              print(f"-> Fetching playlist: {entry.get('title', playlist_url)}")
              try:
                # Fetch the full playlist details including its video entries
                pl_info = ydl.extract_info(playlist_url, download=False)
                if pl_info:
                  pl_title = pl_info.get("title", "unknown_playlist")
                  safe_pl_title = "".join(
                      c
                      for c in pl_title
                      if c.isalnum() or c in (" ", "_", "-")
                  ).strip()

                  file_path = os.path.join(
                      channel_dir, f"{safe_pl_title}.json"
                  )
                  with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(pl_info, f, indent=4)
                  print(f"   Saved playlist JSON with its video entries.")
              except Exception as sub_e:
                print(f"   Error fetching playlist {playlist_url}: {sub_e}")
        else:
          # It's a direct playlist or a video feed (like /videos)
          title = info.get("title", "feed")
          safe_title = "".join(
              c for c in title if c.isalnum() or c in (" ", "_", "-")
          ).strip()

          file_path = os.path.join(channel_dir, f"{safe_title}.json")
          with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)
          print(f"Successfully saved feed/playlist JSON: {safe_title}.json")

      except Exception as e:
        print(f"Error processing {url}: {e}")


if __name__ == "__main__":
  archive_youtube_metadata(TARGET_URLS)
