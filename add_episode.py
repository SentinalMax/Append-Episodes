import os
from mutagen.mp3 import MP3
import xml.etree.ElementTree as ET
import argparse
from datetime import datetime, timezone

def add_episode_to_rss(rss_file_path, mp3_file_path, episode_name, episode_subtitle, episode_description, season_number, episode_number, explicit):
    # Get the current system time in RFC-822 format with UTC timezone
    current_time_rfc822 = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

    # Correct the timezone format to comply with RFC-822 (e.g., converting '+0000' to 'GMT')
    if current_time_rfc822.endswith('+0000'):
        current_time_rfc822 = current_time_rfc822[:-5] + 'GMT'

    # Load RSS XML
    tree = ET.parse(rss_file_path)
    root = tree.getroot()
    channel = root.find('channel')

    # Extract MP3 file name without extension and file size
    file_name = os.path.basename(mp3_file_path)
    file_size = os.path.getsize(mp3_file_path)
    try:
        audio = MP3(mp3_file_path)
        audio_length = int(audio.info.length)
    except Exception as e:
        print(f"Error processing MP3 file: {e}")
        return

    # Format duration in HH:MM:SS
    hours, remainder = divmod(audio_length, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    # Assuming the location of MP3 is a URL path for the file
    mp3_url = f"http://SERVER_IP/mp3s/{file_name}"

    # Create a new item
    new_item = ET.Element('item')
    ET.SubElement(new_item, 'title').text = episode_name
    ET.SubElement(new_item, 'ns1:title').text = episode_name  # Adjusted for correct namespace
    ET.SubElement(new_item, 'ns1:author').text = "AUTHOR"
    ET.SubElement(new_item, 'ns1:subtitle').text = episode_subtitle
    ET.SubElement(new_item, 'ns1:summary').text = episode_description
    ET.SubElement(new_item, 'description').text = episode_description
    ET.SubElement(new_item, 'ns1:image').set('href', "http://SERVER_IP/logo.jpg")
    enclosure = ET.SubElement(new_item, 'enclosure')
    enclosure.set('url', mp3_url)
    enclosure.set('length', str(file_size))
    enclosure.set('type', "audio/mpeg")
    ET.SubElement(new_item, 'ns1:duration').text = duration_formatted
    ET.SubElement(new_item, 'ns1:season').text = season_number
    ET.SubElement(new_item, 'ns1:episode').text = episode_number
    ET.SubElement(new_item, 'ns1:episodeType').text = "full"
    ET.SubElement(new_item, 'guid', isPermaLink="false").text = mp3_url
    ET.SubElement(new_item, 'pubDate').text = current_time_rfc822
    ET.SubElement(new_item, 'ns1:explicit').text = explicit

    # Append the new item to the channel
    channel.append(new_item)

    # Save the modified RSS back to the file
    tree.write(rss_file_path, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add an episode to an RSS feed")
    parser.add_argument("rss_file_path", help="Path to the RSS file")
    parser.add_argument("mp3_file_path", help="Path to the MP3 file")
    parser.add_argument("episode_name", help="Name of the episode")
    parser.add_argument("episode_subtitle", help="Subtitle of the episode")
    parser.add_argument("episode_description", help="Description of the episode")
    parser.add_argument("season_number", help="Season number")
    parser.add_argument("episode_number", help="Episode number")
    parser.add_argument("explicit", choices=['true', 'false'], help="Explicit content (TRUE or FALSE)")

    args = parser.parse_args()

    # Automatically use the current time for the publish date
    add_episode_to_rss(args.rss_file_path, args.mp3_file_path, args.episode_name, args.episode_subtitle, args.episode_description, args.season_number, args.episode_number, args.explicit)