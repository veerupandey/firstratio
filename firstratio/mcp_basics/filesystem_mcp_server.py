from mcp.server.fastmcp import FastMCP
import os
import json
from datetime import datetime
import shutil

# Create a named server
mcp = FastMCP("filesystem-operations")

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """
    List files and directories in the specified path.

    Args:
        path (str): Directory path to list contents from. Defaults to current directory.

    Returns:
        str: JSON string with directory contents or an error message.
    """
    try:
        if not os.path.exists(path):
            return json.dumps({"error": f"Path '{path}' does not exist."})
        
        if not os.path.isdir(path):
            return json.dumps({"error": f"Path '{path}' is not a directory."})
        
        contents = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            
            stats = os.stat(item_path)
            contents.append({
                "name": item,
                "type": item_type,
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
            })
        
        return json.dumps({
            "path": os.path.abspath(path),
            "contents": contents,
            "count": len(contents)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read the contents of a file.

    Args:
        path (str): Path to the file to read.

    Returns:
        str: File contents or an error message in JSON format.
    """
    try:
        if not os.path.exists(path):
            return json.dumps({"error": f"File '{path}' does not exist."})
        
        if not os.path.isfile(path):
            return json.dumps({"error": f"Path '{path}' is not a file."})
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return json.dumps({
                "path": os.path.abspath(path),
                "content": content,
                "size": os.path.getsize(path)
            }, indent=2)
        except UnicodeDecodeError:
            return json.dumps({"error": f"File '{path}' is not a text file or has an unsupported encoding."})
    
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

@mcp.tool()
def write_file(path: str, content: str, mode: str = "w") -> str:
    """
    Write content to a file.

    Args:
        path (str): Path to the file to write to.
        content (str): Content to write to the file.
        mode (str): Write mode ('w' for overwrite, 'a' for append). Defaults to 'w'.

    Returns:
        str: Success or error message in JSON format.
    """
    try:
        if mode not in ('w', 'a'):
            return json.dumps({"error": f"Invalid mode '{mode}'. Use 'w' for overwrite or 'a' for append."})
        
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(path, mode, encoding='utf-8') as file:
            file.write(content)
        
        return json.dumps({
            "status": "success",
            "path": os.path.abspath(path),
            "message": f"Content {'appended to' if mode == 'a' else 'written to'} file successfully.",
            "size": os.path.getsize(path)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

@mcp.tool()
def file_info(path: str) -> str:
    """
    Get detailed information about a file or directory.

    Args:
        path (str): Path to the file or directory.

    Returns:
        str: File information in JSON format or an error message.
    """
    try:
        if not os.path.exists(path):
            return json.dumps({"error": f"Path '{path}' does not exist."})
        
        stats = os.stat(path)
        info = {
            "path": os.path.abspath(path),
            "name": os.path.basename(path),
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
            "permissions": oct(stats.st_mode)[-3:],
        }
        
        return json.dumps(info, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a new directory.

    Args:
        path (str): Path of the directory to create.

    Returns:
        str: Success or error message in JSON format.
    """
    try:
        if os.path.exists(path):
            return json.dumps({"error": f"Path '{path}' already exists."})
        
        os.makedirs(path)
        return json.dumps({
            "status": "success",
            "path": os.path.abspath(path),
            "message": f"Directory created successfully."
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

@mcp.tool()
def delete_item(path: str, recursive: bool = False) -> str:
    """
    Delete a file or directory.

    Args:
        path (str): Path to the file or directory to delete.
        recursive (bool): If True, recursively delete directories. Defaults to False.

    Returns:
        str: Success or error message in JSON format.
    """
    try:
        if not os.path.exists(path):
            return json.dumps({"error": f"Path '{path}' does not exist."})
        
        item_type = "directory" if os.path.isdir(path) else "file"
        
        if item_type == "file":
            os.remove(path)
        else:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        
        return json.dumps({
            "status": "success",
            "path": os.path.abspath(path),
            "type": item_type,
            "message": f"{item_type.capitalize()} deleted successfully."
        }, indent=2)
    
    except OSError as e:
        if "Directory not empty" in str(e):
            return json.dumps({"error": f"Directory '{path}' is not empty. Use recursive=True to delete it and its contents."})
        else:
            return json.dumps({"error": f"An error occurred: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    mcp.run(transport="stdio")