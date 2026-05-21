#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Search Module
Advanced search functionality for bookmarks
"""

import re
from typing import List, Dict
from difflib import SequenceMatcher
from .bookmark import Bookmark


class SearchEngine:
    """Advanced bookmark search engine"""
    
    def __init__(self, database):
        """Initialize search engine with database"""
        self.db = database
    
    def search(self, query: str, search_in: List[str] = None,
               folder: str = None, tags: List[str] = None,
               fuzzy: bool = False) -> List[Dict]:
        """
        Search bookmarks with advanced filters
        
        Args:
            query: Search query string
            search_in: Fields to search in ['title', 'description', 'url', 'tags']
            folder: Filter by folder name
            tags: Filter by tags
            fuzzy: Enable fuzzy matching
        """
        if not search_in:
            search_in = ['title', 'description', 'url', 'tags']
        
        # Get all bookmarks
        all_bookmarks = self.db.list_bookmarks(folder=folder)
        
        if not query.strip():
            # No query, just return filtered by folder/tags
            if tags:
                all_bookmarks = [b for b in all_bookmarks 
                               if any(tag in b.get('tags', []) for tag in tags)]
            return all_bookmarks
        
        # Perform search
        results = []
        query_lower = query.lower()
        
        for bookmark in all_bookmarks:
            score = 0
            matched = False
            
            # Check each search field
            for field in search_in:
                value = bookmark.get(field, '')
                if field == 'tags':
                    value = ' '.join(value) if isinstance(value, list) else str(value)
                else:
                    value = str(value) if value else ''
                
                value_lower = value.lower()
                
                # Exact match (highest score)
                if query_lower == value_lower:
                    score += 100
                    matched = True
                # Starts with query
                elif value_lower.startswith(query_lower):
                    score += 50
                    matched = True
                # Contains query
                elif query_lower in value_lower:
                    score += 25
                    matched = True
                # Fuzzy match
                elif fuzzy:
                    similarity = SequenceMatcher(None, query_lower, value_lower).ratio()
                    if similarity > 0.6:
                        score += int(similarity * 20)
                        matched = True
            
            # Tag filtering
            if tags:
                bookmark_tags = bookmark.get('tags', [])
                if not any(tag in bookmark_tags for tag in tags):
                    matched = False
            
            if matched:
                bookmark['_search_score'] = score
                results.append(bookmark)
        
        # Sort by score (descending) then by created_at
        results.sort(key=lambda x: (-x['_search_score'], x.get('created_at', '')), reverse=False)
        
        return results
    
    def search_by_regex(self, pattern: str, search_in: List[str] = None) -> List[Dict]:
        """Search using regular expression"""
        if not search_in:
            search_in = ['title', 'description', 'url']
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        all_bookmarks = self.db.list_bookmarks()
        results = []
        
        for bookmark in all_bookmarks:
            for field in search_in:
                value = bookmark.get(field, '')
                if field == 'tags':
                    value = ' '.join(value) if isinstance(value, list) else str(value)
                else:
                    value = str(value) if value else ''
                
                if regex.search(value):
                    results.append(bookmark)
                    break
        
        return results
    
    def quick_search(self, query: str) -> List[Dict]:
        """Quick search with default settings"""
        return self.search(query, fuzzy=True)
    
    def find_duplicates(self) -> List[Dict]:
        """Find duplicate bookmarks"""
        return self.db.check_duplicate_urls()
    
    def find_similar(self, bookmark_id: int, threshold: float = 0.7) -> List[Dict]:
        """Find bookmarks similar to given bookmark"""
        target = self.db.get_bookmark(bookmark_id)
        if not target:
            return []
        
        all_bookmarks = self.db.list_bookmarks()
        results = []
        
        target_title = target.get('title', '') or ''
        target_url = target.get('url', '') or ''
        
        for bookmark in all_bookmarks:
            if bookmark['id'] == bookmark_id:
                continue
            
            # Compare titles
            title_sim = SequenceMatcher(None, target_title.lower(),
                                       (bookmark.get('title') or '').lower()).ratio()
            
            # Compare URLs
            url_sim = SequenceMatcher(None, target_url.lower(),
                                     (bookmark.get('url') or '').lower()).ratio()
            
            # Use max similarity
            similarity = max(title_sim, url_sim)
            
            if similarity >= threshold:
                bookmark['_similarity'] = similarity
                results.append(bookmark)
        
        # Sort by similarity
        results.sort(key=lambda x: x['_similarity'], reverse=True)
        return results
