#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Exporter Module
Export bookmarks to various formats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from .bookmark import Bookmark


class BookmarkExporter:
    """Export bookmarks to various formats"""
    
    @staticmethod
    def to_html(bookmarks: List[Bookmark], file_path: str, title: str = "Bookmarks"):
        """Export to Netscape Bookmark HTML format"""
        # Group bookmarks by folder
        folders = {}
        for bookmark in bookmarks:
            folder = bookmark.folder or 'Uncategorized'
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(bookmark)
        
        html_content = f'''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>{title}</TITLE>
<H1>{title}</H1>
<DL><p>
'''
        
        for folder_name, folder_bookmarks in sorted(folders.items()):
            html_content += f'    <DT><H3>{folder_name}</H3>\n'
            html_content += '    <DL><p>\n'
            
            for bookmark in folder_bookmarks:
                tags_attr = ','.join(bookmark.tags) if bookmark.tags else ''
                add_date = ''
                if bookmark.created_at:
                    add_date = f' ADD_DATE="{int(bookmark.created_at.timestamp())}"'
                
                html_content += f'        <DT><A HREF="{bookmark.url}"{add_date} TAGS="{tags_attr}">{bookmark.title or "Untitled"}</A>\n'
            
            html_content += '    </DL><p>\n'
        
        html_content += '</DL><p>\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    @staticmethod
    def to_json(bookmarks: List[Bookmark], file_path: str):
        """Export to JSON format"""
        data = {
            'export_date': datetime.now().isoformat(),
            'total_bookmarks': len(bookmarks),
            'bookmarks': [bookmark.to_dict() for bookmark in bookmarks]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_markdown(bookmarks: List[Bookmark], file_path: str, group_by_folder: bool = True):
        """Export to Markdown format"""
        md_content = f'# Bookmarks\n\n'
        md_content += f'*Exported on {datetime.now().strftime("%Y-%m-%d %H:%M")}*\n\n'
        md_content += f'*Total: {len(bookmarks)} bookmarks*\n\n'
        md_content += '---\n\n'
        
        if group_by_folder:
            # Group by folder
            folders = {}
            for bookmark in bookmarks:
                folder = bookmark.folder or 'Uncategorized'
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(bookmark)
            
            for folder_name in sorted(folders.keys()):
                md_content += f'## {folder_name}\n\n'
                for bookmark in folders[folder_name]:
                    md_content += f'- [{bookmark.title or "Untitled"}]({bookmark.url})\n'
                    if bookmark.description:
                        md_content += f'  - {bookmark.description}\n'
                    if bookmark.tags:
                        tags_str = ' '.join([f'`#{tag}`' for tag in bookmark.tags])
                        md_content += f'  - Tags: {tags_str}\n'
                    md_content += '\n'
        else:
            # Flat list
            for bookmark in bookmarks:
                md_content += f'- [{bookmark.title or "Untitled"}]({bookmark.url})\n'
                if bookmark.description:
                    md_content += f'  - {bookmark.description}\n'
                if bookmark.tags:
                    tags_str = ' '.join([f'`#{tag}`' for tag in bookmark.tags])
                    md_content += f'  - Tags: {tags_str}\n'
                md_content += '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    @staticmethod
    def to_text(bookmarks: List[Bookmark], file_path: str):
        """Export to plain text format"""
        text_content = f'Bookmarks Export\n'
        text_content += f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
        text_content += f'Total: {len(bookmarks)} bookmarks\n'
        text_content += '=' * 50 + '\n\n'
        
        for bookmark in bookmarks:
            text_content += f'Title: {bookmark.title or "Untitled"}\n'
            text_content += f'URL: {bookmark.url}\n'
            if bookmark.folder:
                text_content += f'Folder: {bookmark.folder}\n'
            if bookmark.tags:
                text_content += f'Tags: {", ".join(bookmark.tags)}\n'
            if bookmark.description:
                text_content += f'Description: {bookmark.description}\n'
            text_content += '-' * 50 + '\n\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    @classmethod
    def export_file(cls, bookmarks: List[Bookmark], file_path: str, format_type: str = None):
        """Auto-detect format and export"""
        path = Path(file_path)
        
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
            format_type = format_map.get(ext, 'html')
        
        # Export based on format
        exporters = {
            'html': cls.to_html,
            'json': cls.to_json,
            'markdown': cls.to_markdown,
            'md': cls.to_markdown,
            'text': cls.to_text,
            'txt': cls.to_text
        }
        
        exporter = exporters.get(format_type.lower())
        if not exporter:
            raise ValueError(f"Unsupported format: {format_type}")
        
        exporter(bookmarks, file_path)
