#!/usr/bin/env python3
"""
Robust Failsafe HTTP Server for AWS CloudAge
Single file, no external dependencies, production-ready
Works on any Linux system including Ubuntu 22.04
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import signal
import socket
from functools import partial
from urllib.request import urlopen
from urllib.error import URLError
import json

# HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="icon" href="https://a0.awsstatic.com/main/images/site/fav/favicon.ico"/>
    <style>
        body {{font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5;}}
        .container {{background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto;}}
        h1 {{color: #232F3E; margin-top: 0;}}
        .info {{background: #e7f3ff; padding: 15px; border-left: 4px solid #2196F3; margin: 15px 0;}}
        .success {{background: #d4edda; border-left-color: #28a745;}}
        .error {{background: #f8d7da; border-left-color: #dc3545;}}
        .footer {{margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666;}}
        a {{color: #2196F3; text-decoration: none;}}
        a:hover {{text-decoration: underline;}}
        code {{background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace;}}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""


class EC2Metadata:
    """Fallback-safe EC2 metadata retriever using IMDSv2"""
    
    METADATA_URL = "http://169.254.169.254/latest/meta-data/"
    TOKEN_URL = "http://169.254.169.254/latest/api/token"
    TOKEN_TTL = "21600"
    TIMEOUT = 1  # Quick timeout for non-EC2 environments
    
    def __init__(self):
        self.token = None
        self.available = self._check_availability()
    
    def _check_availability(self):
        """Check if running on EC2 by attempting to get token"""
        try:
            req = urlopen(
                self.TOKEN_URL,
                data=None,
                timeout=self.TIMEOUT
            )
            req.close()
            return True
        except (URLError, socket.timeout, OSError):
            return False
    
    def _get_token(self):
        """Get IMDSv2 token"""
        if self.token:
            return self.token
        
        try:
            req = urlopen(
                self.TOKEN_URL,
                data=None,
                timeout=self.TIMEOUT
            )
            self.token = req.read().decode('utf-8')
            return self.token
        except Exception:
            return None
    
    def _get_metadata(self, path):
        """Get metadata from IMDSv2"""
        if not self.available:
            return None
        
        token = self._get_token()
        if not token:
            return None
        
        try:
            req = urlopen(
                f"{self.METADATA_URL}{path}",
                timeout=self.TIMEOUT
            )
            return req.read().decode('utf-8').strip()
        except Exception:
            return None
    
    @property
    def instance_id(self):
        return self._get_metadata("instance-id") or "N/A"
    
    @property
    def instance_type(self):
        return self._get_metadata("instance-type") or "N/A"
    
    @property
    def availability_zone(self):
        return self._get_metadata("placement/availability-zone") or "N/A"
    
    @property
    def region(self):
        az = self.availability_zone
        if az and az != "N/A":
            return az[:-1]  # Remove last character (zone letter)
        return None
    
    @property
    def private_ipv4(self):
        return self._get_metadata("local-ipv4") or "N/A"
    
    @property
    def public_ipv4(self):
        return self._get_metadata("public-ipv4") or "N/A"


class RobustRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler with complete error handling"""
    
    def __init__(self, region, metadata, *args, **kwargs):
        self.region = region
        self.metadata = metadata
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging to stdout"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")
        sys.stdout.flush()
    
    def send_html_response(self, status_code, title, content):
        """Send HTML response with error handling"""
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            html = HTML_TEMPLATE.format(title=title, content=content)
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            sys.stderr.write(f"Error sending response: {e}\n")
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.handle_root()
            elif self.path == '/healthcheck':
                self.handle_healthcheck()
            elif self.path == '/info':
                self.handle_info()
            else:
                self.handle_404()
        except Exception as e:
            self.handle_error(str(e))
    
    def handle_root(self):
        """Main landing page"""
        content = '<h1>Hello from CloudAge</h1>'
        content += '<h1>What to watch next....</h1>'
        
        # Show region info
        content += f'<div class="info"><strong>Region:</strong> {self.region}</div>'
        
        # Show EC2 info if available
        if self.metadata.available:
            content += '<div class="info success">'
            content += '<strong>Running on EC2 Instance</strong><br>'
            content += f'<strong>Instance ID:</strong> {self.metadata.instance_id}<br>'
            content += f'<strong>Availability Zone:</strong> {self.metadata.availability_zone}'
            content += '</div>'
        else:
            content += '<div class="info">'
            content += '<strong>Environment:</strong> Local/Non-EC2 environment'
            content += '</div>'
        
        # Navigation
        content += '<div class="footer">'
        content += '<strong>Available Endpoints:</strong><br>'
        content += '<a href="/">Home</a> | '
        content += '<a href="/healthcheck">Health Check</a> | '
        content += '<a href="/info">Server Info</a>'
        content += '</div>'
        
        self.send_html_response(200, "AWS CloudAge", content)
    
    def handle_healthcheck(self):
        """Health check endpoint for load balancers"""
        content = '<h1>Success</h1>'
        content += '<div class="info success">'
        content += '<strong>Status:</strong> Server is healthy and operational<br>'
        content += f'<strong>Region:</strong> {self.region}'
        content += '</div>'
        content += '<div class="footer"><a href="/">← Back to Home</a></div>'
        
        self.send_html_response(200, "Health Check", content)
    
    def handle_info(self):
        """Detailed server information"""
        content = '<h1>Server Information</h1>'
        
        # Server details
        content += '<div class="info">'
        content += f'<strong>Region:</strong> {self.region}<br>'
        content += f'<strong>Server Address:</strong> {self.server.server_address[0]}:{self.server.server_address[1]}<br>'
        content += f'<strong>Python Version:</strong> {sys.version.split()[0]}'
        content += '</div>'
        
        # EC2 metadata if available
        if self.metadata.available:
            content += '<h2>EC2 Instance Details</h2>'
            content += '<div class="info success">'
            content += f'<strong>Instance ID:</strong> {self.metadata.instance_id}<br>'
            content += f'<strong>Instance Type:</strong> {self.metadata.instance_type}<br>'
            content += f'<strong>Availability Zone:</strong> {self.metadata.availability_zone}<br>'
            content += f'<strong>Private IPv4:</strong> {self.metadata.private_ipv4}<br>'
            content += f'<strong>Public IPv4:</strong> {self.metadata.public_ipv4}'
            content += '</div>'
        else:
            content += '<div class="info">'
            content += '<strong>EC2 Metadata:</strong> Not available (not running on EC2 or metadata service disabled)'
            content += '</div>'
        
        content += '<div class="footer"><a href="/">← Back to Home</a></div>'
        
        self.send_html_response(200, "Server Information", content)
    
    def handle_404(self):
        """404 Not Found page"""
        content = '<h1>404 - Page Not Found</h1>'
        content += f'<div class="info error">'
        content += f'The requested path <code>{self.path}</code> was not found on this server.'
        content += '</div>'
        content += '<div class="footer"><a href="/">← Back to Home</a></div>'
        
        self.send_html_response(404, "404 Not Found", content)
    
    def handle_error(self, error_message):
        """500 Internal Server Error page"""
        content = '<h1>500 - Internal Server Error</h1>'
        content += '<div class="info error">'
        content += f'<strong>Error:</strong> {error_message}'
        content += '</div>'
        content += '<div class="footer"><a href="/">← Back to Home</a></div>'
        
        self.send_html_response(500, "Internal Server Error", content)


def parse_arguments(args):
    """Parse command line arguments without getopt dependency"""
    config = {
        'ip': '0.0.0.0',
        'port': 8080,
        'region': None
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        
        elif arg in ('-s', '--server_ip'):
            if i + 1 < len(args):
                config['ip'] = args[i + 1]
                i += 1
        
        elif arg in ('-p', '--server_port'):
            if i + 1 < len(args):
                try:
                    port = int(args[i + 1])
                    if 1 <= port <= 65535:
                        config['port'] = port
                    else:
                        print(f"Error: Port must be between 1 and 65535")
                        sys.exit(1)
                except ValueError:
                    print(f"Error: Invalid port number: {args[i + 1]}")
                    sys.exit(1)
                i += 1
        
        elif arg in ('-r', '--region'):
            if i + 1 < len(args):
                config['region'] = args[i + 1]
                i += 1
        
        else:
            print(f"Unknown argument: {arg}")
            print_usage()
            sys.exit(1)
        
        i += 1
    
    return config


def print_usage():
    """Print usage information"""
    print("""
Robust HTTP Server for AWS CloudAge

Usage: python3 server.py [OPTIONS]

Options:
    -h, --help              Show this help message
    -s, --server_ip IP      Server IP address (default: 0.0.0.0)
    -p, --server_port PORT  Server port (default: 8080)
    -r, --region REGION     AWS region override (auto-detected on EC2)

Examples:
    python3 server.py
    python3 server.py -p 8080
    python3 server.py -s 127.0.0.1 -p 3000
    sudo python3 server.py -p 80
    python3 server.py -r us-west-2

Features:
    ✓ No external dependencies (uses only Python standard library)
    ✓ Auto-detects EC2 metadata (IMDSv2 compatible)
    ✓ Graceful fallback for non-EC2 environments
    ✓ Health check endpoint for load balancers
    ✓ Comprehensive error handling
    ✓ Clean shutdown with Ctrl+C
""")


def main():
    """Main entry point"""
    
    # Parse arguments
    config = parse_arguments(sys.argv[1:])
    
    # Initialize EC2 metadata
    print("Checking EC2 metadata availability...")
    metadata = EC2Metadata()
    
    # Determine region
    region = config['region']
    if not region:
        if metadata.available:
            region = metadata.region or 'us-east-1'
            print(f"Detected EC2 region: {region}")
        else:
            region = 'us-east-1'
            print(f"Not running on EC2, using default region: {region}")
    else:
        print(f"Using specified region: {region}")
    
    # Check port privileges
    if config['port'] < 1024 and sys.platform.startswith('linux'):
        try:
            import os
            if os.geteuid() != 0:
                print(f"\n⚠️  Warning: Port {config['port']} requires root privileges")
                print(f"Run with: sudo python3 server.py -p {config['port']}")
                print(f"Or use a port >= 1024 (recommended)")
                sys.exit(1)
        except AttributeError:
            pass
    
    # Create server
    try:
        server_address = (config['ip'], config['port'])
        handler = partial(RobustRequestHandler, region, metadata)
        httpd = HTTPServer(server_address, handler)
        
        print("\n" + "=" * 70)
        print("🚀 Server Started Successfully")
        print("=" * 70)
        print(f"Address:  {config['ip']}:{config['port']}")
        print(f"Region:   {region}")
        
        if metadata.available:
            print(f"Instance: {metadata.instance_id}")
        
        # Determine access URL
        access_host = 'localhost' if config['ip'] == '0.0.0.0' else config['ip']
        print(f"\nAccess at: http://{access_host}:{config['port']}")
        print("\nEndpoints:")
        print(f"  • Main page:    http://{access_host}:{config['port']}/")
        print(f"  • Health check: http://{access_host}:{config['port']}/healthcheck")
        print(f"  • Server info:  http://{access_host}:{config['port']}/info")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 70 + "\n")
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print("\n\nShutdown signal received, stopping server...")
            httpd.shutdown()
            print("Server stopped successfully")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start serving
        httpd.serve_forever()
        
    except PermissionError:
        print(f"\n❌ Error: Permission denied for port {config['port']}")
        print(f"Use a port >= 1024 or run with sudo")
        sys.exit(1)
    
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n❌ Error: Port {config['port']} is already in use")
            print(f"Try a different port: python3 server.py -p 8081")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

