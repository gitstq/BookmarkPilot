#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Formatter Module
Output formatting utilities
"""

import shutil
from datetime import datetime
from typing import List, Dict


class Formatter:
    """Output formatting utilities"""
    
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text"""
        color_code = cls.COLORS.get(color, '')
        reset = cls.COLORS['reset']
        return f"{color_code}{text}{reset}"
    
    @classmethod
    def truncate(cls, text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @classmethod
    def format_bookmark_line(cls, bookmark: Dict, index: int = None,
                            max_width: int = None) -> str:
        """Format bookmark as a single line"""
        if max_width is None:
            max_width = shutil.get_terminal_size().columns
        
        parts = []
        
        # Index
        if index is not None:
            parts.append(cls.colorize(f"[{index:3}]", 'bright_black'))
        
        # Favorite indicator
        if bookmark.get('is_favorite'):
            parts.append(cls.colorize('★', 'bright_yellow'))
        else:
            parts.append(cls.colorize(' ', 'bright_black'))
        
        # Title
        title = bookmark.get('title') or 'Untitled'
        title = cls.truncate(title, 40)
        parts.append(cls.colorize(title, 'bold'))
        
        # URL
        url = bookmark.get('url', '')
        url_display = cls.truncate(url, 40)
        parts.append(cls.colorize(url_display, 'bright_blue'))
        
        # Tags
        tags = bookmark.get('tags', [])
        if tags:
            tags_str = ' '.join([f'#{t}' for t in tags[:3]])
            parts.append(cls.colorize(tags_str, 'bright_cyan'))
        
        # Folder
        folder = bookmark.get('folder', 'Uncategorized')
        parts.append(cls.colorize(f'[{folder}]', 'bright_black'))
        
        line = ' '.join(parts)
        return cls.truncate(line, max_width)
    
    @classmethod
    def format_bookmark_detail(cls, bookmark: Dict) -> str:
        """Format bookmark with full details"""
        lines = []
        
        # Header
        title = bookmark.get('title') or 'Untitled'
        fav = '★ ' if bookmark.get('is_favorite') else ''
        lines.append(cls.colorize(f"{fav}{title}", 'bold'))
        lines.append(cls.colorize('=' * 50, 'bright_black'))
        
        # URL
        url = bookmark.get('url', '')
        lines.append(f"{cls.colorize('URL:', 'bright_cyan')} {cls.colorize(url, 'bright_blue')}")
        
        # Description
        desc = bookmark.get('description')
        if desc:
            lines.append(f"{cls.colorize('Description:', 'bright_cyan')} {desc}")
        
        # Folder
        folder = bookmark.get('folder', 'Uncategorized')
        lines.append(f"{cls.colorize('Folder:', 'bright_cyan')} {folder}")
        
        # Tags
        tags = bookmark.get('tags', [])
        if tags:
            tags_str = ' '.join([f'#{t}' for t in tags])
            lines.append(f"{cls.colorize('Tags:', 'bright_cyan')} {tags_str}")
        
        # Stats
        visit_count = bookmark.get('visit_count', 0)
        lines.append(f"{cls.colorize('Visits:', 'bright_cyan')} {visit_count}")
        
        # Dates
        created = bookmark.get('created_at', '')
        if created:
            lines.append(f"{cls.colorize('Created:', 'bright_cyan')} {created}")
        
        updated = bookmark.get('updated_at', '')
        if updated and updated != created:
            lines.append(f"{cls.colorize('Updated:', 'bright_cyan')} {updated}")
        
        return '\n'.join(lines)
    
    @classmethod
    def format_stats(cls, stats: Dict) -> str:
        """Format statistics output"""
        lines = []
        
        lines.append(cls.colorize('📊 Bookmark Statistics', 'bold'))
        lines.append(cls.colorize('=' * 40, 'bright_black'))
        
        lines.append(f"{cls.colorize('Total Bookmarks:', 'bright_cyan')} {stats.get('total_bookmarks', 0)}")
        lines.append(f"{cls.colorize('Favorites:', 'bright_yellow')} {stats.get('favorites', 0)}")
        lines.append(f"{cls.colorize('Archived:', 'bright_black')} {stats.get('archived_bookmarks', 0)}")
        lines.append(f"{cls.colorize('Folders:', 'bright_green')} {stats.get('folders', 0)}")
        lines.append(f"{cls.colorize('Tags:', 'bright_magenta')} {stats.get('total_tags', 0)}")
        
        # Most visited
        most_visited = stats.get('most_visited', [])
        if most_visited:
            lines.append('')
            lines.append(cls.colorize('🔥 Most Visited:', 'bright_yellow'))
            for item in most_visited[:5]:
                title = item.get('title', 'Untitled')
                count = item.get('visit_count', 0)
                lines.append(f"  {title} ({count} visits)")
        
        # Recent additions
        recent = stats.get('recent_additions', [])
        if recent:
            lines.append('')
            lines.append(cls.colorize('🆕 Recent Additions:', 'bright_green'))
            for item in recent[:5]:
                title = item.get('title', 'Untitled')
                lines.append(f"  {title}")
        
        return '\n'.join(lines)
    
    @classmethod
    def format_table(cls, headers: List[str], rows: List[List[str]],
                     max_width: int = None) -> str:
        """Format data as a table"""
        if max_width is None:
            max_width = shutil.get_terminal_size().columns
        
        if not rows:
            return "No data"
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Limit total width
        total_width = sum(col_widths) + 3 * (len(headers) - 1)
        if total_width > max_width:
            # Reduce column widths proportionally
            factor = (max_width - 3 * (len(headers) - 1)) / sum(col_widths)
            col_widths = [int(w * factor) for w in col_widths]
        
        lines = []
        
        # Header
        header_cells = [cls.colorize(cls.truncate(h, w), 'bold') 
                       for h, w in zip(headers, col_widths)]
        lines.append(' | '.join(header_cells))
        lines.append('-' * min(total_width, max_width))
        
        # Rows
        for row in rows:
            row_cells = [cls.truncate(str(cell), w) 
                        for cell, w in zip(row, col_widths)]
            lines.append(' | '.join(row_cells))
        
        return '\n'.join(lines)
    
    @classmethod
    def format_list(cls, items: List[str], bullet: str = '•') -> str:
        """Format items as a bulleted list"""
        return '\n'.join([f"{bullet} {item}" for item in items])
    
    @classmethod
    def success(cls, message: str) -> str:
        """Format success message"""
        return cls.colorize(f"✓ {message}", 'bright_green')
    
    @classmethod
    def error(cls, message: str) -> str:
        """Format error message"""
        return cls.colorize(f"✗ {message}", 'bright_red')
    
    @classmethod
    def warning(cls, message: str) -> str:
        """Format warning message"""
        return cls.colorize(f"⚠ {message}", 'bright_yellow')
    
    @classmethod
    def info(cls, message: str) -> str:
        """Format info message"""
        return cls.colorize(f"ℹ {message}", 'bright_cyan')
