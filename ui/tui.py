#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot TUI Module
Terminal User Interface
"""

import sys
import os
import shutil
from typing import List, Dict, Optional

# Fix imports for direct execution
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database
from core.search import SearchEngine
from utils.formatter import Formatter


class TUI:
    """Terminal User Interface for BookmarkPilot"""
    
    def __init__(self, database: Database):
        """Initialize TUI"""
        self.db = database
        self.search = SearchEngine(database)
        self.formatter = Formatter()
        self.current_bookmarks = []
        self.selected_index = 0
        self.search_query = ''
        self.current_folder = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def get_terminal_size(self):
        """Get terminal dimensions"""
        return shutil.get_terminal_size()
    
    def print_header(self):
        """Print application header"""
        width = self.get_terminal_size().columns
        title = "BookmarkPilot"
        subtitle = "Terminal Bookmark Manager"
        
        print(self.formatter.colorize(title.center(width), 'bold'))
        print(self.formatter.colorize(subtitle.center(width), 'bright_black'))
        print(self.formatter.colorize('=' * width, 'bright_black'))
    
    def print_status_bar(self):
        """Print status bar"""
        width = self.get_terminal_size().columns
        
        stats = self.db.get_stats()
        status = f"Total: {stats['total_bookmarks']} | Favorites: {stats['favorites']} | Folders: {stats['folders']}"
        
        if self.search_query:
            status += f" | Search: '{self.search_query}'"
        if self.current_folder:
            status += f" | Folder: {self.current_folder}"
        
        print(self.formatter.colorize(status.ljust(width), 'bright_black'))
        print(self.formatter.colorize('-' * width, 'bright_black'))
    
    def print_bookmark_list(self):
        """Print list of bookmarks"""
        if not self.current_bookmarks:
            print(self.formatter.colorize("\n  No bookmarks found.\n", 'bright_black'))
            return
        
        height = self.get_terminal_size().lines
        max_display = height - 10  # Reserve space for header, status, etc.
        
        # Calculate visible range
        total = len(self.current_bookmarks)
        start = max(0, self.selected_index - max_display // 2)
        end = min(total, start + max_display)
        
        # Adjust start if at end of list
        if end - start < max_display:
            start = max(0, end - max_display)
        
        print()
        for i in range(start, end):
            bookmark = self.current_bookmarks[i]
            
            # Format line
            prefix = "> " if i == self.selected_index else "  "
            line = self.formatter.format_bookmark_line(bookmark, i + 1)
            
            # Highlight selected
            if i == self.selected_index:
                line = self.formatter.colorize(line, 'bright_white')
            
            print(f"{prefix}{line}")
        
        print()
        print(self.formatter.colorize(f"  Showing {start+1}-{end} of {total}", 'bright_black'))
    
    def print_help(self):
        """Print help information"""
        help_text = """
Commands:
  ↑/↓ or j/k    Navigate bookmarks
  Enter         Open selected bookmark
  /             Search
  f             Filter by folder
  t             Filter by tag
  a             Add new bookmark
  e             Edit selected bookmark
  d             Delete selected bookmark
  s             Toggle favorite
  r             Refresh list
  q             Quit
"""
        print(help_text)
    
    def load_bookmarks(self):
        """Load bookmarks into list"""
        if self.search_query:
            self.current_bookmarks = self.search.quick_search(self.search_query)
        else:
            self.current_bookmarks = self.db.list_bookmarks(folder=self.current_folder)
        
        # Ensure selected index is valid
        if self.selected_index >= len(self.current_bookmarks):
            self.selected_index = max(0, len(self.current_bookmarks) - 1)
    
    def open_bookmark(self, bookmark: Dict):
        """Open bookmark URL in browser"""
        url = bookmark.get('url', '')
        if url:
            # Increment visit count
            self.db.increment_visit_count(bookmark['id'])
            
            # Open URL
            browser = 'xdg-open'
            if os.name == 'nt':  # Windows
                os.system(f'start "" "{url}"')
            elif os.name == 'darwin':  # macOS
                os.system(f'open "{url}"')
            else:  # Linux
                os.system(f'xdg-open "{url}" 2>/dev/null &')
            
            print(self.formatter.success(f"Opened: {url}"))
    
    def prompt_input(self, prompt: str, default: str = '') -> str:
        """Get user input"""
        try:
            if default:
                response = input(f"{prompt} [{default}]: ").strip()
                return response if response else default
            else:
                return input(f"{prompt}: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ''
    
    def add_bookmark_interactive(self):
        """Interactive bookmark addition"""
        print(self.formatter.colorize("\n📌 Add New Bookmark\n", 'bold'))
        
        url = self.prompt_input("URL")
        if not url:
            print(self.formatter.warning("Cancelled"))
            return
        
        title = self.prompt_input("Title (optional)")
        description = self.prompt_input("Description (optional)")
        folder = self.prompt_input("Folder", 'Uncategorized')
        tags_input = self.prompt_input("Tags (comma-separated)")
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
        
        try:
            bookmark_id = self.db.add_bookmark(url, title, description, folder, tags)
            print(self.formatter.success(f"Bookmark added (ID: {bookmark_id})"))
            self.load_bookmarks()
        except Exception as e:
            print(self.formatter.error(f"Failed to add bookmark: {e}"))
    
    def edit_bookmark_interactive(self):
        """Interactive bookmark editing"""
        if not self.current_bookmarks:
            print(self.formatter.warning("No bookmark selected"))
            return
        
        bookmark = self.current_bookmarks[self.selected_index]
        print(self.formatter.colorize(f"\n✏️  Edit Bookmark (ID: {bookmark['id']})\n", 'bold'))
        
        title = self.prompt_input("Title", bookmark.get('title', ''))
        description = self.prompt_input("Description", bookmark.get('description', ''))
        folder = self.prompt_input("Folder", bookmark.get('folder', 'Uncategorized'))
        tags_str = ', '.join(bookmark.get('tags', []))
        tags_input = self.prompt_input("Tags", tags_str)
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
        
        try:
            self.db.update_bookmark(
                bookmark['id'],
                title=title,
                description=description,
                folder=folder,
                tags=tags
            )
            print(self.formatter.success("Bookmark updated"))
            self.load_bookmarks()
        except Exception as e:
            print(self.formatter.error(f"Failed to update bookmark: {e}"))
    
    def delete_bookmark_interactive(self):
        """Interactive bookmark deletion"""
        if not self.current_bookmarks:
            print(self.formatter.warning("No bookmark selected"))
            return
        
        bookmark = self.current_bookmarks[self.selected_index]
        title = bookmark.get('title', 'Untitled')
        
        confirm = self.prompt_input(f"Delete '{title}'? (y/N)")
        if confirm.lower() == 'y':
            try:
                self.db.delete_bookmark(bookmark['id'])
                print(self.formatter.success("Bookmark deleted"))
                self.load_bookmarks()
            except Exception as e:
                print(self.formatter.error(f"Failed to delete bookmark: {e}"))
        else:
            print(self.formatter.info("Cancelled"))
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        if not self.current_bookmarks:
            return
        
        bookmark = self.current_bookmarks[self.selected_index]
        new_status = not bookmark.get('is_favorite', False)
        
        try:
            self.db.update_bookmark(bookmark['id'], is_favorite=new_status)
            bookmark['is_favorite'] = new_status
            status = "added to" if new_status else "removed from"
            print(self.formatter.success(f"Bookmark {status} favorites"))
        except Exception as e:
            print(self.formatter.error(f"Failed to update: {e}"))
    
    def search_interactive(self):
        """Interactive search"""
        query = self.prompt_input("Search query")
        self.search_query = query
        self.current_folder = None
        self.selected_index = 0
        self.load_bookmarks()
    
    def filter_folder_interactive(self):
        """Interactive folder filter"""
        folders = self.db.get_folders()
        
        if not folders:
            print(self.formatter.warning("No folders found"))
            return
        
        print(self.formatter.colorize("\n📁 Available Folders:\n", 'bold'))
        for i, folder in enumerate(folders, 1):
            print(f"  {i}. {folder}")
        print("  0. All folders")
        
        choice = self.prompt_input("Select folder")
        
        if choice == '0':
            self.current_folder = None
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                self.current_folder = folders[idx]
        
        self.search_query = ''
        self.selected_index = 0
        self.load_bookmarks()
    
    def filter_tag_interactive(self):
        """Interactive tag filter"""
        tags = self.db.get_all_tags()
        
        if not tags:
            print(self.formatter.warning("No tags found"))
            return
        
        print(self.formatter.colorize("\n🏷️  Available Tags:\n", 'bold'))
        for i, tag in enumerate(tags, 1):
            print(f"  {i}. #{tag}")
        
        tag_input = self.prompt_input("Enter tag name(s)")
        selected_tags = [t.strip() for t in tag_input.split(',') if t.strip()]
        
        if selected_tags:
            self.current_bookmarks = [
                b for b in self.db.list_bookmarks()
                if any(t in b.get('tags', []) for t in selected_tags)
            ]
            self.selected_index = 0
    
    def run(self):
        """Run TUI main loop"""
        self.load_bookmarks()
        
        while True:
            self.clear_screen()
            self.print_header()
            self.print_status_bar()
            self.print_bookmark_list()
            
            try:
                # Get single character input
                if os.name == 'nt':
                    import msvcrt
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                else:
                    import tty
                    import termios
                    
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        key = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                # Handle key presses
                if key in ['q', 'Q']:
                    break
                elif key in ['j', 'J']:
                    if self.selected_index < len(self.current_bookmarks) - 1:
                        self.selected_index += 1
                elif key in ['k', 'K']:
                    if self.selected_index > 0:
                        self.selected_index -= 1
                elif key == '\r':  # Enter
                    if self.current_bookmarks:
                        self.open_bookmark(self.current_bookmarks[self.selected_index])
                        input("\nPress Enter to continue...")
                elif key == '/':
                    self.search_interactive()
                elif key in ['f', 'F']:
                    self.filter_folder_interactive()
                elif key in ['t', 'T']:
                    self.filter_tag_interactive()
                elif key in ['a', 'A']:
                    self.add_bookmark_interactive()
                    input("\nPress Enter to continue...")
                elif key in ['e', 'E']:
                    self.edit_bookmark_interactive()
                    input("\nPress Enter to continue...")
                elif key in ['d', 'D']:
                    self.delete_bookmark_interactive()
                    input("\nPress Enter to continue...")
                elif key in ['s', 'S']:
                    self.toggle_favorite()
                elif key in ['r', 'R']:
                    self.load_bookmarks()
                elif key == 'h' or key == '?':
                    self.print_help()
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(self.formatter.error(f"Error: {e}"))
                input("\nPress Enter to continue...")
        
        print(self.formatter.colorize("\nGoodbye!\n", 'bright_green'))


if __name__ == '__main__':
    # Test TUI
    db = Database()
    tui = TUI(db)
    tui.run()
