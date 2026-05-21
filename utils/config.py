#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Config Module
Configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager"""
    
    DEFAULT_CONFIG = {
        'database_path': None,  # Use default location
        'default_folder': 'Uncategorized',
        'editor': None,  # Auto-detect
        'browser': None,  # Auto-detect
        'ui': {
            'theme': 'default',
            'show_favicons': True,
            'items_per_page': 20
        },
        'search': {
            'default_fields': ['title', 'description', 'url', 'tags'],
            'fuzzy_threshold': 0.6,
            'case_sensitive': False
        },
        'import': {
            'skip_duplicates': True,
            'default_folder': 'Imported'
        },
        'export': {
            'default_format': 'html',
            'include_metadata': True
        }
    }
    
    def __init__(self):
        """Initialize configuration"""
        self.config_dir = Path.home() / '.bookmarkpilot'
        self.config_file = self.config_dir / 'config.json'
        self.config = {}
        self._load()
    
    def _load(self):
        """Load configuration from file"""
        self.config_dir.mkdir(exist_ok=True)
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                self.config = {}
        
        # Merge with defaults
        self._merge_defaults()
    
    def _merge_defaults(self):
        """Merge config with defaults"""
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self.config[key]:
                        self.config[key][sub_key] = sub_value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def get_database_path(self) -> str:
        """Get database file path"""
        path = self.get('database_path')
        if path:
            return path
        return str(self.config_dir / 'bookmarks.db')
    
    def get_editor(self) -> str:
        """Get preferred editor"""
        editor = self.get('editor')
        if editor:
            return editor
        
        # Auto-detect
        for env_var in ['EDITOR', 'VISUAL']:
            if env_var in os.environ:
                return os.environ[env_var]
        
        # Default editors
        editors = ['nano', 'vim', 'vi']
        for ed in editors:
            if os.system(f'which {ed} > /dev/null 2>&1') == 0:
                return ed
        
        return 'nano'
    
    def get_browser(self) -> str:
        """Get preferred browser"""
        browser = self.get('browser')
        if browser:
            return browser
        
        # Auto-detect
        for env_var in ['BROWSER']:
            if env_var in os.environ:
                return os.environ[env_var]
        
        # Default browsers
        browsers = ['xdg-open', 'open', 'firefox', 'chrome', 'chromium']
        for br in browsers:
            if os.system(f'which {br} > /dev/null 2>&1') == 0:
                return br
        
        return 'xdg-open'
    
    def reset(self):
        """Reset to default configuration"""
        self.config = {}
        self._merge_defaults()
        self.save()
