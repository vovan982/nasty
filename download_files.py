import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download.log'),
        logging.StreamHandler()
    ]
)

class FileDownloader:
    def __init__(self, base_url, output_dir='downloaded_files'):
        self.base_url = base_url
        self.output_dir = output_dir
        self.downloaded_files = set()
        self.session = requests.Session()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Set a reasonable timeout
        self.session.timeout = (10, 30)  # (connect timeout, read timeout)
        
    def is_valid_url(self, url):
        """Check if the URL is valid and belongs to the same domain."""
        try:
            result = urlparse(url)
            base_domain = urlparse(self.base_url).netloc
            return bool(result.netloc) and result.netloc == base_domain
        except:
            return False
            
    def get_absolute_url(self, url):
        """Convert relative URL to absolute URL."""
        return urljoin(self.base_url, url)
        
    def download_file(self, url):
        """Download a single file."""
        if url in self.downloaded_files:
            return
            
        try:
            # Get the file name from the URL
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"file_{int(time.time())}"
                
            filepath = os.path.join(self.output_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                logging.info(f"File already exists: {filename}")
                self.downloaded_files.add(url)
                return
                
            # Download the file
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            logging.info(f"Successfully downloaded: {filename}")
            self.downloaded_files.add(url)
            
        except Exception as e:
            logging.error(f"Error downloading {url}: {str(e)}")
            
    def find_files(self, url):
        """Find all downloadable files on a page."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links and resources
            files = set()
            
            # Check for <a> tags with href
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(href.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.jpg', '.jpeg', '.png', '.gif']):
                    abs_url = self.get_absolute_url(href)
                    if self.is_valid_url(abs_url):
                        files.add(abs_url)
                        
            # Check for <img> tags
            for img in soup.find_all('img', src=True):
                src = img['src']
                abs_url = self.get_absolute_url(src)
                if self.is_valid_url(abs_url):
                    files.add(abs_url)
                    
            # Check for <link> tags (CSS, etc.)
            for link in soup.find_all('link', href=True):
                href = link['href']
                abs_url = self.get_absolute_url(href)
                if self.is_valid_url(abs_url):
                    files.add(abs_url)
                    
            # Check for <script> tags
            for script in soup.find_all('script', src=True):
                src = script['src']
                abs_url = self.get_absolute_url(src)
                if self.is_valid_url(abs_url):
                    files.add(abs_url)
                    
            return files
            
        except Exception as e:
            logging.error(f"Error finding files on {url}: {str(e)}")
            return set()
            
    def download_all_files(self, max_workers=5):
        """Download all files found on the website."""
        files = self.find_files(self.base_url)
        logging.info(f"Found {len(files)} files to download")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.download_file, files)
            
        logging.info("Download process completed")

def main():
    # Example usage
    website_url = input("Enter the website URL: ")
    output_directory = input("Enter output directory (press Enter for default 'downloaded_files'): ") or 'downloaded_files'
    
    downloader = FileDownloader(website_url, output_directory)
    downloader.download_all_files()

if __name__ == "__main__":
    main() 