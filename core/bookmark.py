#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Bookmark Model
Bookmark data structure and validation
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import re


@dataclass
class Bookmark:
    """Bookmark data model"""
    
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    folder: str = 'Uncategorized'
    tags: List[str] = field(default_factory=list)
    favicon: Optional[str] = None
    visit_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_archived: bool = False
    is_favorite: bool = False
    id: Optional[int] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.title is None:
            self.title = self._extract_title_from_url()
    
    def _extract_title_from_url(self) -> str:
        """Extract a readable title from URL"""
        try:
            # Remove protocol
            url = re.sub(r'^https?://', '', self.url)
            # Remove www
            url = re.sub(r'^www\.', '', url)
            # Get domain and path
            parts = url.split('/')
            domain = parts[0]
            # Capitalize and clean
            title = domain.replace('-', ' ').replace('_', ' ').title()
            return title
        except:
            return self.url
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(pattern.match(url))
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        # Remove trailing slash
        url = url.rstrip('/')
        return url
    
    def add_tag(self, tag: str):
        """Add a tag"""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag"""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'folder': self.folder,
            'tags': self.tags,
            'favicon': self.favicon,
            'visit_count': self.visit_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_archived': self.is_archived,
            'is_favorite': self.is_favorite
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Bookmark':
        """Create Bookmark from dictionary"""
        bookmark = cls(
            url=data['url'],
            title=data.get('title'),
            description=data.get('description'),
            folder=data.get('folder', 'Uncategorized'),
            tags=data.get('tags', []),
            favicon=data.get('favicon'),
            visit_count=data.get('visit_count', 0),
            is_archived=data.get('is_archived', False),
            is_favorite=data.get('is_favorite', False),
            id=data.get('id')
        )
        
        # Parse dates
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                bookmark.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], str):
                bookmark.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return bookmark
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.title or 'Untitled'} ({self.url})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"<Bookmark id={self.id} title='{self.title}' url='{self.url}'>"
