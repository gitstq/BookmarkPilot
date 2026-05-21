#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot - Lightweight Terminal Bookmark Manager

A zero-dependency terminal bookmark management tool for developers.
Manage your browser bookmarks, code snippets, and documentation links with ease.
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.bookmark import Bookmark
from core.importer import BookmarkImporter
from core.exporter import BookmarkExporter
from core.search import SearchEngine
from ui.tui import TUI
from utils.config import Config
from utils.formatter import Formatter
from utils.validator import URLValidator


__version__ = '1.0.0'
__author__ = 'BookmarkPilot Team'


def init_config():
    """Initialize configuration"""
    return Config()


def init_database(config: Config):
    """Initialize database connection"""
    db_path = config.get_database_path()
    return Database(db_path)


def cmd_add(args, db: Database, formatter: Formatter):
    """Add a new bookmark"""
    url = args.url
    
    # Validate URL
    if not URLValidator.is_valid(url):
        print(formatter.error(f"Invalid URL: {url}"))
        return 1
    
    url = URLValidator.normalize(url)
    
    # Check for duplicates
    existing = db.get_bookmark_by_url(url)
    if existing:
        print(formatter.warning(f"Bookmark already exists (ID: {existing['id']})"))
        return 1
    
    # Add bookmark
    try:
        bookmark_id = db.add_bookmark(
            url=url,
            title=args.title,
            description=args.description,
            folder=args.folder or 'Uncategorized',
            tags=args.tags.split(',') if args.tags else [],
            is_favorite=args.favorite
        )
        print(formatter.success(f"Bookmark added (ID: {bookmark_id})"))
        return 0
    except Exception as e:
        print(formatter.error(f"Failed to add bookmark: {e}"))
        return 1


def cmd_list(args, db: Database, formatter: Formatter):
    """List bookmarks"""
    bookmarks = db.list_bookmarks(
        folder=args.folder,
        archived=args.archived,
        favorite_only=args.favorite,
        limit=args.limit
    )
    
    if not bookmarks:
        print(formatter.info("No bookmarks found"))
        return 0
    
    print(formatter.colorize(f"\n📚 Bookmarks ({len(bookmarks)} total)\n", 'bold'))
    
    for i, bookmark in enumerate(bookmarks, 1):
        print(formatter.format_bookmark_line(bookmark, i))
    
    print()
    return 0


def cmd_search(args, db: Database, formatter: Formatter):
    """Search bookmarks"""
    search = SearchEngine(db)
    
    results = search.search(
        query=args.query,
        folder=args.folder,
        fuzzy=args.fuzzy
    )
    
    if not results:
        print(formatter.info(f"No results found for '{args.query}'"))
        return 0
    
    print(formatter.colorize(f"\n🔍 Search Results for '{args.query}' ({len(results)} found)\n", 'bold'))
    
    for i, bookmark in enumerate(results, 1):
        print(formatter.format_bookmark_line(bookmark, i))
    
    print()
    return 0


def cmd_show(args, db: Database, formatter: Formatter):
    """Show bookmark details"""
    bookmark = db.get_bookmark(args.id)
    
    if not bookmark:
        print(formatter.error(f"Bookmark not found (ID: {args.id})"))
        return 1
    
    print()
    print(formatter.format_bookmark_detail(bookmark))
    print()
    return 0


def cmd_edit(args, db: Database, formatter: Formatter):
    """Edit a bookmark"""
    bookmark = db.get_bookmark(args.id)
    
    if not bookmark:
        print(formatter.error(f"Bookmark not found (ID: {args.id})"))
        return 1
    
    updates = {}
    if args.title is not None:
        updates['title'] = args.title
    if args.description is not None:
        updates['description'] = args.description
    if args.folder is not None:
        updates['folder'] = args.folder
    if args.tags is not None:
        updates['tags'] = args.tags.split(',') if args.tags else []
    if args.favorite is not None:
        updates['is_favorite'] = args.favorite
    if args.archive is not None:
        updates['is_archived'] = args.archive
    
    if not updates:
        print(formatter.warning("No changes specified"))
        return 1
    
    try:
        db.update_bookmark(args.id, **updates)
        print(formatter.success(f"Bookmark updated (ID: {args.id})"))
        return 0
    except Exception as e:
        print(formatter.error(f"Failed to update bookmark: {e}"))
        return 1


def cmd_delete(args, db: Database, formatter: Formatter):
    """Delete a bookmark"""
    bookmark = db.get_bookmark(args.id)
    
    if not bookmark:
        print(formatter.error(f"Bookmark not found (ID: {args.id})"))
        return 1
    
    if not args.force:
        title = bookmark.get('title', 'Untitled')
        confirm = input(f"Delete '{title}'? (y/N): ")
        if confirm.lower() != 'y':
            print(formatter.info("Cancelled"))
            return 0
    
    try:
        db.delete_bookmark(args.id)
        print(formatter.success(f"Bookmark deleted (ID: {args.id})"))
        return 0
    except Exception as e:
        print(formatter.error(f"Failed to delete bookmark: {e}"))
        return 1


def cmd_import(args, db: Database, formatter: Formatter):
    """Import bookmarks from file"""
    if not os.path.exists(args.file):
        print(formatter.error(f"File not found: {args.file}"))
        return 1
    
    try:
        bookmarks = BookmarkImporter.import_file(args.file, args.format)
        
        if not bookmarks:
            print(formatter.warning("No bookmarks found in file"))
            return 1
        
        # Add to database
        added = 0
        skipped = 0
        folder = args.folder or 'Imported'
        
        for bookmark in bookmarks:
            # Check for duplicates
            if args.skip_duplicates:
                existing = db.get_bookmark_by_url(bookmark.url)
                if existing:
                    skipped += 1
                    continue
            
            # Override folder if specified
            if args.folder:
                bookmark.folder = args.folder
            
            try:
                db.add_bookmark(
                    url=bookmark.url,
                    title=bookmark.title,
                    description=bookmark.description,
                    folder=bookmark.folder,
                    tags=bookmark.tags
                )
                added += 1
            except Exception as e:
                print(formatter.warning(f"Skipped {bookmark.url}: {e}"))
                skipped += 1
        
        print(formatter.success(f"Imported {added} bookmarks, skipped {skipped}"))
        return 0
        
    except Exception as e:
        print(formatter.error(f"Import failed: {e}"))
        return 1


def cmd_export(args, db: Database, formatter: Formatter):
    """Export bookmarks to file"""
    bookmarks_data = db.list_bookmarks(folder=args.folder)
    bookmarks = [Bookmark.from_dict(b) for b in bookmarks_data]
    
    if not bookmarks:
        print(formatter.warning("No bookmarks to export"))
        return 1
    
    try:
        BookmarkExporter.export_file(bookmarks, args.file, args.format)
        print(formatter.success(f"Exported {len(bookmarks)} bookmarks to {args.file}"))
        return 0
    except Exception as e:
        print(formatter.error(f"Export failed: {e}"))
        return 1


def cmd_stats(args, db: Database, formatter: Formatter):
    """Show statistics"""
    stats = db.get_stats()
    print()
    print(formatter.format_stats(stats))
    print()
    return 0


def cmd_folders(args, db: Database, formatter: Formatter):
    """List folders"""
    folders = db.get_folders()
    
    if not folders:
        print(formatter.info("No folders found"))
        return 0
    
    print(formatter.colorize("\n📁 Folders:\n", 'bold'))
    for folder in folders:
        count = len(db.list_bookmarks(folder=folder))
        print(f"  • {folder} ({count} bookmarks)")
    print()
    return 0


def cmd_tags(args, db: Database, formatter: Formatter):
    """List tags"""
    tags = db.get_all_tags()
    
    if not tags:
        print(formatter.info("No tags found"))
        return 0
    
    print(formatter.colorize("\n🏷️  Tags:\n", 'bold'))
    for tag in tags:
        print(f"  #{tag}")
    print()
    return 0


def cmd_open(args, db: Database, formatter: Formatter):
    """Open bookmark URL"""
    bookmark = db.get_bookmark(args.id)
    
    if not bookmark:
        print(formatter.error(f"Bookmark not found (ID: {args.id})"))
        return 1
    
    url = bookmark.get('url', '')
    if not url:
        print(formatter.error("Bookmark has no URL"))
        return 1
    
    # Increment visit count
    db.increment_visit_count(args.id)
    
    # Open URL
    if os.name == 'nt':  # Windows
        os.system(f'start "" "{url}"')
    elif os.name == 'darwin':  # macOS
        os.system(f'open "{url}"')
    else:  # Linux
        os.system(f'xdg-open "{url}" 2>/dev/null &')
    
    print(formatter.success(f"Opened: {url}"))
    return 0


def cmd_check(args, db: Database, formatter: Formatter):
    """Check for duplicate or broken links"""
    if args.duplicates:
        duplicates = db.check_duplicate_urls()
        if duplicates:
            print(formatter.colorize("\n⚠️  Duplicate URLs found:\n", 'bright_yellow'))
            for dup in duplicates:
                print(f"  {dup['url']} ({dup['count']} occurrences)")
            print()
        else:
            print(formatter.success("No duplicate URLs found"))
        return 0
    
    if args.broken:
        print(formatter.info("Checking for broken links... (this may take a while)"))
        bookmarks = db.list_bookmarks()
        broken = []
        
        for bookmark in bookmarks:
            url = bookmark.get('url', '')
            is_accessible, status, error = URLValidator.check_accessibility(url, timeout=10)
            if not is_accessible:
                broken.append({
                    'id': bookmark['id'],
                    'title': bookmark.get('title', 'Untitled'),
                    'url': url,
                    'status': status,
                    'error': error
                })
        
        if broken:
            print(formatter.colorize(f"\n⚠️  {len(broken)} broken links found:\n", 'bright_yellow'))
            for item in broken:
                print(f"  [{item['id']}] {item['title']}")
                print(f"      URL: {item['url']}")
                if item['status']:
                    print(f"      Status: {item['status']}")
                print()
        else:
            print(formatter.success("No broken links found"))
        return 0
    
    print(formatter.warning("Use --duplicates or --broken"))
    return 1


def cmd_tui(args, db: Database, formatter: Formatter):
    """Launch TUI mode"""
    try:
        tui = TUI(db)
        tui.run()
        return 0
    except Exception as e:
        print(formatter.error(f"TUI error: {e}"))
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog='bookmarkpilot',
        description='BookmarkPilot - Terminal Bookmark Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bookmarkpilot add https://github.com "GitHub" --tags git,dev
  bookmarkpilot list --folder Work
  bookmarkpilot search "python tutorial"
  bookmarkpilot import bookmarks.html --format html
  bookmarkpilot export bookmarks.json --format json
  bookmarkpilot tui
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--config', help='Path to config file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new bookmark')
    add_parser.add_argument('url', help='Bookmark URL')
    add_parser.add_argument('title', nargs='?', help='Bookmark title')
    add_parser.add_argument('--description', '-d', help='Bookmark description')
    add_parser.add_argument('--folder', '-f', help='Folder name')
    add_parser.add_argument('--tags', '-t', help='Comma-separated tags')
    add_parser.add_argument('--favorite', action='store_true', help='Mark as favorite')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List bookmarks')
    list_parser.add_argument('--folder', '-f', help='Filter by folder')
    list_parser.add_argument('--favorite', action='store_true', help='Show favorites only')
    list_parser.add_argument('--archived', action='store_true', help='Show archived')
    list_parser.add_argument('--limit', '-n', type=int, help='Limit results')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search bookmarks')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--folder', '-f', help='Filter by folder')
    search_parser.add_argument('--fuzzy', action='store_true', help='Enable fuzzy search')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show bookmark details')
    show_parser.add_argument('id', type=int, help='Bookmark ID')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a bookmark')
    edit_parser.add_argument('id', type=int, help='Bookmark ID')
    edit_parser.add_argument('--title', help='New title')
    edit_parser.add_argument('--description', '-d', help='New description')
    edit_parser.add_argument('--folder', '-f', help='New folder')
    edit_parser.add_argument('--tags', '-t', help='New comma-separated tags')
    edit_parser.add_argument('--favorite', type=lambda x: x.lower() == 'true',
                            help='Set favorite status (true/false)')
    edit_parser.add_argument('--archive', type=lambda x: x.lower() == 'true',
                            help='Set archive status (true/false)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a bookmark')
    delete_parser.add_argument('id', type=int, help='Bookmark ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import bookmarks')
    import_parser.add_argument('file', help='File to import')
    import_parser.add_argument('--format', choices=['html', 'json', 'markdown', 'text'],
                              help='File format (auto-detect if not specified)')
    import_parser.add_argument('--folder', '-f', help='Import to folder')
    import_parser.add_argument('--skip-duplicates', action='store_true',
                              default=True, help='Skip duplicate URLs')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export bookmarks')
    export_parser.add_argument('file', help='Output file')
    export_parser.add_argument('--format', choices=['html', 'json', 'markdown', 'text'],
                              help='Export format (auto-detect if not specified)')
    export_parser.add_argument('--folder', '-f', help='Export folder only')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Folders command
    subparsers.add_parser('folders', help='List folders')
    
    # Tags command
    subparsers.add_parser('tags', help='List tags')
    
    # Open command
    open_parser = subparsers.add_parser('open', help='Open bookmark URL')
    open_parser.add_argument('id', type=int, help='Bookmark ID')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check bookmarks')
    check_parser.add_argument('--duplicates', action='store_true', help='Find duplicates')
    check_parser.add_argument('--broken', action='store_true', help='Find broken links')
    
    # TUI command
    subparsers.add_parser('tui', help='Launch TUI mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize
    config = init_config()
    db = init_database(config)
    formatter = Formatter()
    
    try:
        # Route to command handler
        commands = {
            'add': cmd_add,
            'list': cmd_list,
            'search': cmd_search,
            'show': cmd_show,
            'edit': cmd_edit,
            'delete': cmd_delete,
            'import': cmd_import,
            'export': cmd_export,
            'stats': cmd_stats,
            'folders': cmd_folders,
            'tags': cmd_tags,
            'open': cmd_open,
            'check': cmd_check,
            'tui': cmd_tui,
        }
        
        handler = commands.get(args.command)
        if handler:
            return handler(args, db, formatter)
        else:
            print(formatter.error(f"Unknown command: {args.command}"))
            return 1
            
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
