import random
import datetime
from faker import Faker
import boto3
import os
from multiprocessing import Pool, cpu_count
import tempfile
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogGenerator:
    def __init__(self):
        self.faker = Faker()
        self.setup_distributions()
        
    def setup_distributions(self):
        """Configure data distributions for realistic log data"""
        self.STATUS_CODES = [
            {'code': 200, 'weight': 0.70},
            {'code': 404, 'weight': 0.15},
            {'code': 500, 'weight': 0.05},
            {'code': 301, 'weight': 0.05},
            {'code': 403, 'weight': 0.03},
            {'code': 503, 'weight': 0.02}
        ]
        
        self.METHODS = [
            {'method': 'GET', 'weight': 0.65},
            {'method': 'POST', 'weight': 0.20},
            {'method': 'PUT', 'weight': 0.08},
            {'method': 'DELETE', 'weight': 0.05},
            {'method': 'HEAD', 'weight': 0.02}
        ]
        
        self.OS_BROWSERS = [
            {'os': 'Windows 10', 'browser': 'Chrome', 'version': '120.0', 'weight': 0.35},
            {'os': 'Windows 11', 'browser': 'Chrome', 'version': '121.0', 'weight': 0.25},
            {'os': 'Mac OS X', 'browser': 'Safari', 'version': '16.0', 'weight': 0.15},
            {'os': 'Linux', 'browser': 'Firefox', 'version': '115.0', 'weight': 0.10},
            {'os': 'iOS', 'browser': 'Mobile Safari', 'version': '16.0', 'weight': 0.08},
            {'os': 'Android', 'browser': 'Chrome Mobile', 'version': '120.0', 'weight': 0.07}
        ]
        
        self.URIS = [
            {'uri': '/index.html', 'weight': 0.25},
            {'uri': '/products', 'weight': 0.15},
            {'uri': '/search', 'weight': 0.15},
            {'uri': '/api/v1/data', 'weight': 0.10},
            {'uri': '/images/logo.png', 'weight': 0.10},
            {'uri': '/static/main.css', 'weight': 0.10},
            {'uri': '/contact', 'weight': 0.08},
            {'uri': '/about', 'weight': 0.07}
        ]
        
        self.LOCATIONS = [
            {'location': 'US', 'weight': 0.50},
            {'location': 'EU', 'weight': 0.30},
            {'location': 'APAC', 'weight': 0.15},
            {'location': 'LATAM', 'weight': 0.05}
        ]
        
        self.BYTE_SIZES = [
            {'min': 100, 'max': 500, 'weight': 0.30},
            {'min': 501, 'max': 5000, 'weight': 0.50},
            {'min': 5001, 'max': 50000, 'weight': 0.15},
            {'min': 50001, 'max': 200000, 'weight': 0.05}
        ]

    def weighted_choice(self, choices):
        """Select an item based on weights"""
        total = sum(item['weight'] for item in choices)
        r = random.uniform(0, total)
        upto = 0
        for item in choices:
            if upto + item['weight'] >= r:
                return item
            upto += item['weight']
        return choices[-1]

    def generate_log_entry(self):
        """Generate a single log entry matching the exact regex pattern"""
        date_obj = self.faker.date_between(start_date='-1y', end_date='today')
        time_str = self.faker.time()
        
        location = self.weighted_choice(self.LOCATIONS)['location']
        byte_size = self.weighted_choice(self.BYTE_SIZES)
        bytes_sent = random.randint(byte_size['min'], byte_size['max'])
        ip = self.faker.ipv4()
        method = self.weighted_choice(self.METHODS)['method']
        host = self.faker.domain_name()
        uri = self.weighted_choice(self.URIS)['uri']
        status = self.weighted_choice(self.STATUS_CODES)['code']
        referrer = self.faker.uri() if random.random() > 0.3 else '-'
        
        browser_info = self.weighted_choice(self.OS_BROWSERS)
        os = browser_info['os']
        browser = browser_info['browser']
        version = browser_info['version']
        
        # Format to match the exact regex pattern
        log_entry = (
            f"{date_obj} {time_str} {location} {bytes_sent} {ip} "
            f"{method} {host} {uri} {status} {referrer} "
            f"some-data({os}; {browser} {version})%20{browser}/{version}"
        )
        return log_entry

def generate_chunk(args):
    """Generate a chunk of log data (for parallel processing)"""
    chunk_size, chunk_num = args
    generator = LogGenerator()
    entries = []
    for _ in range(chunk_size):
        entries.append(generator.generate_log_entry() + '\n')
    return chunk_num, ''.join(entries)

class S3Uploader:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
        
    def upload_file(self, file_path, s3_key):
        """Upload file to S3 with progress tracking"""
        try:
            file_size = os.path.getsize(file_path)
            with tqdm(total=file_size, unit='B', unit_scale=True, 
                     desc=f"Uploading {os.path.basename(file_path)}") as pbar:
                self.s3.upload_file(
                    file_path,
                    self.bucket,
                    s3_key,
                    Callback=lambda bytes_transferred: pbar.update(bytes_transferred)
                )
            logger.info(f"Successfully uploaded {file_path} to s3://{self.bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return False

def generate_log_data(target_size_gb, output_path, s3_bucket=None, s3_prefix=None):
    """Generate log data with progress tracking and optional S3 upload"""
    target_bytes = int(target_size_gb * 1024 ** 3)
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "application_logs.txt")
    
    logger.info(f"Generating {target_size_gb}GB of log data...")
    
    # Calculate chunk size for parallel generation
    chunk_size = 1000  # entries per chunk
    total_entries_estimate = int(target_bytes / 200)  # avg entry size ~200 bytes
    num_chunks = (total_entries_estimate // chunk_size) + 1
    
    # Generate data in parallel
    with Pool(processes=cpu_count()) as pool:
        chunks = [(chunk_size, i) for i in range(num_chunks)]
        results = []
        
        with tqdm(total=num_chunks, desc="Generating chunks") as pbar:
            for result in pool.imap_unordered(generate_chunk, chunks):
                results.append(result)
                pbar.update(1)
        
        # Sort chunks and write to file
        results.sort(key=lambda x: x[0])
        with open(temp_file, 'w') as f:
            for chunk_num, data in results:
                f.write(data)
                if f.tell() >= target_bytes:
                    break
    
    final_size = os.path.getsize(temp_file) / (1024 ** 3)
    logger.info(f"Generated {final_size:.2f}GB of data in {temp_file}")
    
    # Upload to S3 if configured
    if s3_bucket and s3_prefix:
        uploader = S3Uploader(s3_bucket)
        s3_key = f"{s3_prefix.rstrip('/')}/application_logs.txt"
        if uploader.upload_file(temp_file, s3_key):
            logger.info(f"Data successfully uploaded to s3://{s3_bucket}/{s3_key}")
            os.remove(temp_file)
            os.rmdir(temp_dir)
            return f"s3://{s3_bucket}/{s3_key}"
    
    return temp_file

if __name__ == "__main__":
    # Configuration
    TARGET_SIZE_GB = 1
    OUTPUT_PATH = "./application_logs.log"  # Local path for generated logs
    S3_BUCKET = "cloudage.llc"  # Set to None for local only
    S3_PREFIX = "data/"  # S3 path prefix
    
    # Generate data
    result_path = generate_log_data(
        target_size_gb=TARGET_SIZE_GB,
        output_path=OUTPUT_PATH,
        s3_bucket=S3_BUCKET,
        s3_prefix=S3_PREFIX
    )
    
    print(f"\nData generation complete. Result stored at: {result_path}")
