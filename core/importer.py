#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Importer Module
Import bookmarks from various formats
"""

import re
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Dict, Optional
from .bookmark import Bookmark


class BookmarkHTMLParser(HTMLParser):
    """Parse Netscape Bookmark HTML format"""
    
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = 'Uncategorized'
        self.in_dt = False
        self.current_data = {}
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'h3':
            self.in_dt = True
        elif tag == 'a' and 'href' in attrs_dict:
            self.current_data = {
                'url': attrs_dict['href'],
                'title': '',
                'folder': self.current_folder,
                'tags': [],
                'add_date': attrs_dict.get('add_date'),
                'icon': attrs_dict.get('icon')
            }
            if 'tags' in attrs_dict:
                self.current_data['tags'] = attrs_dict['tags'].split(',')
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.current_data:
            self.bookmarks.append(self.current_data)
            self.current_data = {}
        elif tag == 'dl':
            self.current_folder = 'Uncategorized'
    
    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.in_dt:
                self.current_folder = data
                self.in_dt = False
            elif self.current_data is not None:
                self.current_data['title'] = data


class BookmarkImporter:
    """Import bookmarks from various formats"""
    
    @staticmethod
    def from_html(file_path: str) -> List[Bookmark]:
        """Import bookmarks from Netscape HTML format"""
        bookmarks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            parser = BookmarkHTMLParser()
            parser.feed(content)
            
            for data in parser.bookmarks:
                try:
                    bookmark = Bookmark(
                        url=Bookmark.normalize_url(data['url']),
                        title=data.get('title', 'Untitled'),
                        folder=data.get('folder', 'Uncategorized'),
                        tags=data.get('tags', [])
                    )
                    bookmarks.append(bookmark)
                except Exception as e:
                    print(f"Warning: Skipped invalid bookmark: {data.get('url', 'unknown')} - {e}")
            
        except Exception as e:
            raise ImportError(f"Failed to import HTML: {e}")
        
        return bookmarks
    
    @staticmethod
    def from_json(file_path: str) -> List[Bookmark]:
        """Import bookmarks from JSON format"""
        bookmarks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get('bookmarks', [])
            else:
                items = []
            
            for item in items:
                try:
                    bookmark = Bookmark.from_dict(item)
                    bookmarks.append(bookmark)
                except Exception as e:
                    print(f"Warning: Skipped invalid bookmark: {e}")
            
        except Exception as e:
            raise ImportError(f"Failed to import JSON: {e}")
        
        return bookmarks
    
    @staticmethod
    def from_markdown(file_path: str) -> List[Bookmark]:
        """Import bookmarks from Markdown link list"""
        bookmarks = []
        current_folder = 'Uncategorized'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Check for folder header
                if line.startswith('# '):
                    current_folder = line[2:].strip()
                    continue
                elif line.startswith('## '):
                    current_folder = line[3:].strip()
                    continue
                
                # Parse markdown link: [title](url)
                match = re.match(r'\[(.+?)\]\((.+?)\)', line)
                if match:
                    title = match.group(1)
                    url = match.group(2)
                    
                    try:
                        bookmark = Bookmark(
                            url=Bookmark.normalize_url(url),
                            title=title,
                            folder=current_folder
                        )
                        bookmarks.append(bookmark)
                    except Exception as e:
                        print(f"Warning: Skipped invalid URL: {url}")
                
                # Parse plain URL
                elif line.startswith('http'):
                    try:
                        bookmark = Bookmark(
                            url=Bookmark.normalize_url(line),
                            folder=current_folder
                        )
                        bookmarks.append(bookmark)
                    except Exception as e:
                        print(f"Warning: Skipped invalid URL: {line}")
            
        except Exception as e:
            raise ImportError(f"Failed to import Markdown: {e}")
        
        return bookmarks
    
    @staticmethod
    def from_text(file_path: str) -> List[Bookmark]:
        """Import bookmarks from plain text (one URL per line)"""
        bookmarks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check if line contains URL
                    url_match = re.search(r'https?://\S+', line)
                    if url_match:
                        url = url_match.group(0)
                        # Try to extract title from the rest of the line
                        rest = line.replace(url, '').strip()
                        title = rest if rest else None
                        
                        try:
                            bookmark = Bookmark(
                                url=Bookmark.normalize_url(url),
                                title=title
                            )
                            bookmarks.append(bookmark)
                        except Exception as e:
                            print(f"Warning: Skipped invalid URL: {url}")
            
        except Exception as e:
            raise ImportError(f"Failed to import text: {e}")
        
        return bookmarks
    
    @classmethod
    def import_file(cls, file_path: str, format_type: str = None) -> List[Bookmark]:
        """Auto-detect and import from file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect format from extension
        if format_type is None:
            ext = path.suffix.lower()
            format_map = {
                '.html': 'html',
                '.htm': 'html',
                '.json': 'json',
                '.md': 'markdown',
                '.markdown': 'markdown',
                '.txt': 'text'
            }
            format_type = format_map.get(ext, 'text')
        
        # Import based on format
        importers = {
            'html': cls.from_html,
            'json': cls.from_json,
            'markdown': cls.from_markdown,
            'md': cls.from_markdown,
            'text': cls.from_text,
            'txt': cls.from_text
        }
        
        importer = importers.get(format_type.lower())
        if not importer:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return importer(file_path)
