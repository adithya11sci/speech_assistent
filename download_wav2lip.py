"""
Download Wav2Lip checkpoint from alternative sources
"""
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url, destination):
    """Download file with progress bar"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)
    
    print(f"✅ Download complete: {destination}")

# Alternative download URLs (try these in order)
alternative_urls = [
    # GitHub releases or mirrors
    "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
    # You can add more mirrors here
]

destination = Path("models/wav2lip/wav2lip_gan.pth")

print("=" * 70)
print("Wav2Lip Checkpoint Downloader")
print("=" * 70)

for i, url in enumerate(alternative_urls, 1):
    try:
        print(f"\nAttempt {i}/{len(alternative_urls)}")
        download_file(url, destination)
        print("\n✅ SUCCESS! Wav2Lip checkpoint downloaded.")
        break
    except Exception as e:
        print(f"❌ Failed: {e}")
        if i == len(alternative_urls):
            print("\n" + "=" * 70)
            print("⚠️  MANUAL DOWNLOAD REQUIRED")
            print("=" * 70)
            print("\nPlease download manually:")
            print("1. Visit: https://github.com/Rudrabha/Wav2Lip")
            print("2. Look for 'Getting the weights' section")
            print("3. Download 'wav2lip_gan.pth' from Google Drive")
            print("4. Save it to: models/wav2lip/wav2lip_gan.pth")
            print("\nOr try this direct link:")
            print("https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1")
