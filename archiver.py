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

        channel_name = info.get(
            "uploader",
            info.get("channel", info.get("title", "unknown_channel")),
        )
        channel_dir = "".join(
            c for c in channel_name if c.isalnum() or c in (" ", "_", "-")
        ).strip()
        os.makedirs(channel_dir, exist_ok=True)
        print(f"Saving files to directory: ./{channel_dir}/")

        if "entries" in info:
          count = 0
          for entry in info["entries"]:
            if entry:
              title = entry.get("title", f"item_{count}")
              safe_title = "".join(
                  c for c in title if c.isalnum() or c in (" ", "_", "-")
              ).strip()

              file_path = os.path.join(channel_dir, f"{safe_title}.json")
              with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=4)
              count += 1
          print(f"Successfully saved {count} JSON files.")
        else:
          title = info.get("title", "video")
          safe_title = "".join(
              c for c in title if c.isalnum() or c in (" ", "_", "-")
          ).strip()
          file_path = os.path.join(channel_dir, f"{safe_title}.json")
          with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)
          print("Successfully saved 1 JSON file.")

      except Exception as e:
        print(f"Error processing {url}: {e}")


if __name__ == "__main__":
  archive_youtube_metadata(TARGET_URLS)