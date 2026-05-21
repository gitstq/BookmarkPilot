#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot URL Validator Module
URL validation and normalization utilities
"""

import re
import urllib.request
import urllib.error
from urllib.parse import urlparse


class URLValidator:
    """URL validation utilities"""
    
    # URL pattern regex
    URL_PATTERN = re.compile(
        r'^(https?://)?'  # protocol
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    @classmethod
    def is_valid(cls, url: str) -> bool:
        """Check if URL is valid"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if not url:
            return False
        
        # Add protocol if missing for validation
        test_url = url
        if not test_url.startswith(('http://', 'https://')):
            test_url = 'https://' + test_url
        
        return bool(cls.URL_PATTERN.match(test_url))
    
    @classmethod
    def normalize(cls, url: str) -> str:
        """Normalize URL"""
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Remove www. prefix for consistency
        # url = re.sub(r'https?://www\.', r'https://', url)
        
        return url
    
    @classmethod
    def get_domain(cls, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(cls.normalize(url))
            return parsed.netloc
        except:
            return ''
    
    @classmethod
    def get_favicon_url(cls, url: str) -> str:
        """Get favicon URL for a website"""
        domain = cls.get_domain(url)
        if domain:
            return f'https://www.google.com/s2/favicons?domain={domain}'
        return ''
    
    @classmethod
    def check_accessibility(cls, url: str, timeout: int = 10) -> tuple:
        """
        Check if URL is accessible
        
        Returns:
            tuple: (is_accessible, status_code, error_message)
        """
        try:
            url = cls.normalize(url)
            
            # Create request with user agent
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                method='HEAD'
            )
            
            response = urllib.request.urlopen(req, timeout=timeout)
            return True, response.getcode(), None
            
        except urllib.error.HTTPError as e:
            # HTTP error (4xx, 5xx)
            if e.code in [403, 405]:  # Forbidden or Method Not Allowed
                # Try GET request instead
                try:
                    req = urllib.request.Request(
                        url,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    response = urllib.request.urlopen(req, timeout=timeout)
                    return True, response.getcode(), None
                except:
                    pass
            return False, e.code, str(e)
            
        except urllib.error.URLError as e:
            return False, None, str(e.reason)
            
        except Exception as e:
            return False, None, str(e)
    
    @classmethod
    def extract_title_from_html(cls, url: str, timeout: int = 10) -> str:
        """Try to extract title from webpage"""
        try:
            url = cls.normalize(url)
            
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                # Extract title
                match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Clean up title
                    title = re.sub(r'\s+', ' ', title)
                    return title
                    
        except Exception as e:
            pass
        
        return ''
