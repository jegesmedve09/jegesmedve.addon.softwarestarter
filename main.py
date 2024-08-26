import xbmcplugin
import xbmcgui
import xbmcaddon
import os
import sys
import subprocess

# Initial argument check
if len(sys.argv) < 2:
    xbmcgui.Dialog().notification('Error', 'This script must be run from within Kodi as a plugin.', xbmcgui.NOTIFICATION_ERROR, 5000)
    sys.exit()

# Plugin handle
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

# Path to the text file containing file paths
addon_path = addon.getAddonInfo('path')
paths_file = os.path.join(addon_path, 'paths.txt')

# Function to read paths from the file
def read_paths():
    if not os.path.exists(paths_file):
        return []  # If the file doesn't exist, return an empty list
    with open(paths_file, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Function to write paths back to the file
def write_paths(paths):
    with open(paths_file, 'w') as file:
        file.write("\n".join(paths) + "\n")

# Function to create a list item for each file
def list_items():
    paths = read_paths()
    xbmcplugin.setContent(handle, 'files')  # Set content type to files
    
    if paths:
        for path in paths:
            if os.path.isfile(path):  # Check if the path is a file
                # Create a list item with the file name
                list_item = xbmcgui.ListItem(label=os.path.basename(path))
                #list_item.setArt({"icon": "resources/icon.png", "thumb": "resources/icon.png"})
                list_item.setInfo("video", {"title": os.path.basename(path)})

                # Set the path to the file as a URL to pass to run
                url = f"plugin://jegesmedve.addon.softwarestarter/?action=run&path={path}"
                xbmcplugin.addDirectoryItem(handle, url, list_item, False)
    else:
        xbmcgui.Dialog().notification('Info', 'No files found in the list.', xbmcgui.NOTIFICATION_INFO, 5000)

    # Add special list item to add a new file
    add_item = xbmcgui.ListItem(label="[Add to list]")
    add_url = "plugin://jegesmedve.addon.softwarestarter/?action=add"
    xbmcplugin.addDirectoryItem(handle, add_url, add_item, False)

    # Add special list item to remove a file
    remove_item = xbmcgui.ListItem(label="[Remove from list]")
    remove_url = "plugin://jegesmedve.addon.softwarestarter/?action=remove"
    xbmcplugin.addDirectoryItem(handle, remove_url, remove_item, False)

    xbmcplugin.endOfDirectory(handle)

# Function to run the selected file
def run_file(path):
    if os.path.isfile(path):
        try:
            # Change directory to the file's directory
            file_dir = os.path.dirname(path)
            os.chdir(file_dir)
            
            # Execute the file
            subprocess.Popen([path], shell=True)
            xbmcgui.Dialog().notification('Execution Started', f'Running {path}', xbmcgui.NOTIFICATION_INFO, 5000)
        except Exception as e:
            xbmcgui.Dialog().notification('Error', str(e), xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        xbmcgui.Dialog().notification('Error', 'File not found', xbmcgui.NOTIFICATION_ERROR, 5000)

# Function to add a new file to the list
def add_to_list():
    dialog = xbmcgui.Dialog()
    path = dialog.browse(1, 'Select a file to add', 'files', '', False, False)
    if path:
        paths = read_paths()
        if path not in paths:
            paths.append(path)
            write_paths(paths)
            xbmcgui.Dialog().notification('Success', 'File added to the list', xbmcgui.NOTIFICATION_INFO, 5000)
        else:
            xbmcgui.Dialog().notification('Error', 'File already in the list', xbmcgui.NOTIFICATION_ERROR, 5000)

# Function to remove a file from the list
def remove_from_list():
    paths = read_paths()
    if not paths:
        xbmcgui.Dialog().notification('Error', 'No files to remove', xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    # Show a selection dialog with current file names
    dialog = xbmcgui.Dialog()
    selection = dialog.select('Select a file to remove', [os.path.basename(path) for path in paths])
    if selection >= 0:
        path_to_remove = paths[selection]
        paths.remove(path_to_remove)
        write_paths(paths)
        xbmcgui.Dialog().notification('Success', 'File removed from the list', xbmcgui.NOTIFICATION_INFO, 5000)

# Main execution logic
if __name__ == '__main__':
    # Check for URL arguments
    args = sys.argv[2][1:]
    if args.startswith('action=run&path='):
        path = args.split('=')[2]
        run_file(path)
    elif args == 'action=add':
        add_to_list()
    elif args == 'action=remove':
        remove_from_list()
    else:
        list_items()
