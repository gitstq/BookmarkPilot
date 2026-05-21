#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Database Module
SQLite database operations for bookmark management
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Database:
    """SQLite database manager for bookmarks"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            config_dir = Path.home() / '.bookmarkpilot'
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / 'bookmarks.db'
        
        self.db_path = str(db_path)
        self.conn = None
        self.cursor = None
        self._connect()
        self._init_tables()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _init_tables(self):
        """Initialize database tables"""
        # Bookmarks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                description TEXT,
                folder TEXT DEFAULT 'Uncategorized',
                tags TEXT DEFAULT '[]',
                favicon TEXT,
                visit_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_archived INTEGER DEFAULT 0,
                is_favorite INTEGER DEFAULT 0
            )
        ''')
        
        # Folders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                parent_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES folders(id)
            )
        ''')
        
        # Insert default folder
        self.cursor.execute('''
            INSERT OR IGNORE INTO folders (name) VALUES ('Uncategorized')
        ''')
        
        self.conn.commit()
    
    def add_bookmark(self, url: str, title: str = None, description: str = None,
                     folder: str = 'Uncategorized', tags: List[str] = None,
                     is_favorite: bool = False) -> int:
        """Add a new bookmark"""
        tags_json = json.dumps(tags or [])
        
        self.cursor.execute('''
            INSERT INTO bookmarks (url, title, description, folder, tags, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, bookmarks.title),
                description = COALESCE(EXCLUDED.description, bookmarks.description),
                folder = EXCLUDED.folder,
                tags = EXCLUDED.tags,
                updated_at = CURRENT_TIMESTAMP
        ''', (url, title, description, folder, tags_json, int(is_favorite)))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_bookmark(self, bookmark_id: int) -> Optional[Dict]:
        """Get a bookmark by ID"""
        self.cursor.execute('SELECT * FROM bookmarks WHERE id = ?', (bookmark_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_bookmark_by_url(self, url: str) -> Optional[Dict]:
        """Get a bookmark by URL"""
        self.cursor.execute('SELECT * FROM bookmarks WHERE url = ?', (url,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def update_bookmark(self, bookmark_id: int, **kwargs) -> bool:
        """Update bookmark fields"""
        allowed_fields = ['url', 'title', 'description', 'folder', 'tags', 
                         'is_archived', 'is_favorite']
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                if key == 'tags' and isinstance(value, list):
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(bookmark_id)
        
        query = f"UPDATE bookmarks SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark"""
        self.cursor.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def list_bookmarks(self, folder: str = None, archived: bool = False,
                       favorite_only: bool = False, limit: int = None) -> List[Dict]:
        """List bookmarks with filters"""
        query = 'SELECT * FROM bookmarks WHERE is_archived = ?'
        params = [int(archived)]
        
        if folder:
            query += ' AND folder = ?'
            params.append(folder)
        
        if favorite_only:
            query += ' AND is_favorite = 1'
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def search_bookmarks(self, query: str, search_in: List[str] = None) -> List[Dict]:
        """Search bookmarks"""
        if not search_in:
            search_in = ['title', 'description', 'url', 'tags']
        
        search_pattern = f'%{query}%'
        conditions = []
        params = []
        
        for field in search_in:
            if field == 'tags':
                conditions.append(f"tags LIKE ?")
            else:
                conditions.append(f"{field} LIKE ?")
            params.append(search_pattern)
        
        query_str = f'''
            SELECT * FROM bookmarks 
            WHERE is_archived = 0 AND ({' OR '.join(conditions)})
            ORDER BY 
                CASE WHEN title LIKE ? THEN 1 ELSE 2 END,
                created_at DESC
        '''
        params.append(search_pattern)
        
        self.cursor.execute(query_str, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def get_folders(self) -> List[str]:
        """Get all folder names"""
        self.cursor.execute('SELECT DISTINCT folder FROM bookmarks ORDER BY folder')
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        self.cursor.execute('SELECT tags FROM bookmarks')
        all_tags = set()
        for row in self.cursor.fetchall():
            tags = json.loads(row[0])
            all_tags.update(tags)
        return sorted(list(all_tags))
    
    def increment_visit_count(self, bookmark_id: int):
        """Increment visit counter"""
        self.cursor.execute('''
            UPDATE bookmarks SET visit_count = visit_count + 1 
            WHERE id = ?
        ''', (bookmark_id,))
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Total bookmarks
        self.cursor.execute('SELECT COUNT(*) FROM bookmarks WHERE is_archived = 0')
        stats['total_bookmarks'] = self.cursor.fetchone()[0]
        
        # Archived bookmarks
        self.cursor.execute('SELECT COUNT(*) FROM bookmarks WHERE is_archived = 1')
        stats['archived_bookmarks'] = self.cursor.fetchone()[0]
        
        # Favorites
        self.cursor.execute('SELECT COUNT(*) FROM bookmarks WHERE is_favorite = 1')
        stats['favorites'] = self.cursor.fetchone()[0]
        
        # Folder count
        self.cursor.execute('SELECT COUNT(DISTINCT folder) FROM bookmarks')
        stats['folders'] = self.cursor.fetchone()[0]
        
        # Tag count
        stats['total_tags'] = len(self.get_all_tags())
        
        # Most visited
        self.cursor.execute('''
            SELECT title, url, visit_count FROM bookmarks 
            WHERE visit_count > 0 
            ORDER BY visit_count DESC LIMIT 5
        ''')
        stats['most_visited'] = [dict(row) for row in self.cursor.fetchall()]
        
        # Recent additions
        self.cursor.execute('''
            SELECT title, url, created_at FROM bookmarks 
            ORDER BY created_at DESC LIMIT 5
        ''')
        stats['recent_additions'] = [dict(row) for row in self.cursor.fetchall()]
        
        return stats
    
    def check_duplicate_urls(self) -> List[Dict]:
        """Find duplicate URLs"""
        self.cursor.execute('''
            SELECT url, COUNT(*) as count 
            FROM bookmarks 
            GROUP BY url 
            HAVING count > 1
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to dictionary"""
        result = dict(row)
        result['tags'] = json.loads(result.get('tags', '[]'))
        result['is_archived'] = bool(result.get('is_archived', 0))
        result['is_favorite'] = bool(result.get('is_favorite', 0))
        return result
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
