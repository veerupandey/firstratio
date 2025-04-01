"""
MCP Server for Git Repository Analysis and Manipulation
====================================================

This module provides a FastMCP server implementation for Git repository operations,
including cloning, analysis, and file manipulation.

The server provides tools for:
- Repository cloning with authentication
- Repository structure and history analysis
- Git command execution
- File reading and writing operations
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from tempfile import gettempdir

from mcp.server.fastmcp import FastMCP
from git import Repo, GitCommandError
import gitlab

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("git-analysis")

# Configuration
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
TEMP_DIR = Path(os.getenv("TEMP_DIR", gettempdir() + "/mcp-git-analysis"))

# Ensure temp directory exists
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def get_repo_dir(repo_url: str) -> Path:
    """
    Get the local directory path for a repository.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository.

    Returns
    -------
    Path
        Path object representing the local directory for the repository.

    Notes
    -----
    The directory name is derived from the repository URL by taking
    the last component and removing the .git extension.
    """
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    return TEMP_DIR / repo_name

@mcp.tool()
def clone_repository(repo_url: str, use_token: bool = True) -> Dict:
    """
    Clone a Git repository with optional token authentication.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository to clone.
    use_token : bool, optional
        Whether to use GitLab token authentication, by default True.

    Returns
    -------
    Dict
        Dictionary containing:
        - status: str, Operation status ('success')
        - action: str, Action performed ('cloned' or 'updated')
        - path: str, Path to the local repository
        - branch: str, Name of the active branch

    Raises
    ------
    Exception
        If cloning fails or if GitLab token is required but not available.

    Notes
    -----
    If the repository already exists locally, it will be updated instead
    of cloned again. For private repositories, set use_token=True and
    ensure GITLAB_TOKEN environment variable is set.
    """
    try:
        repo_dir = get_repo_dir(repo_url)
        
        if use_token and GITLAB_TOKEN:
            url_parts = repo_url.split("://")
            repo_url = f"{url_parts[0]}://oauth2:{GITLAB_TOKEN}@{url_parts[1]}"
        
        if repo_dir.exists():
            repo = Repo(repo_dir)
            repo.remotes.origin.pull()
            action = "updated"
        else:
            repo = Repo.clone_from(repo_url, repo_dir)
            action = "cloned"
            
        return {
            'status': 'success',
            'action': action,
            'path': str(repo_dir),
            'branch': repo.active_branch.name
        }
    except Exception as e:
        raise Exception(f"Failed to clone repository: {str(e)}")

@mcp.tool()
def analyze_repository(repo_url: str) -> Dict:
    """
    Perform comprehensive analysis of a Git repository.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository to analyze.

    Returns
    -------
    Dict
        Dictionary containing:
        - commits: List[Dict], Recent commit information
        - branches: List[Dict], Branch information
        - structure: List[Dict], Repository file structure
        - active_branch: str, Name of the active branch
        - remotes: List[str], List of remote names

    Raises
    ------
    Exception
        If repository is not found or analysis fails.

    Notes
    -----
    The analysis includes:
    - Last 10 commits with author and message
    - All branches and their latest commits
    - Complete directory structure (excluding .git)
    - Remote repository information
    """
    repo_dir = get_repo_dir(repo_url)
    if not repo_dir.exists():
        raise Exception("Repository not found. Clone it first.")
    
    try:
        repo = Repo(repo_dir)
        
        commits = [{
            'hash': c.hexsha,
            'author': c.author.name,
            'date': datetime.fromtimestamp(c.authored_date).isoformat(),
            'message': c.message.strip()
        } for c in repo.iter_commits(max_count=10)]
        
        branches = [{
            'name': b.name,
            'is_active': b.name == repo.active_branch.name,
            'last_commit': b.commit.hexsha
        } for b in repo.branches]
        
        def get_directory_structure(path: Path, prefix: str = "") -> List[Dict]:
            """
            Recursively build directory structure.

            Parameters
            ----------
            path : Path
                Directory path to analyze
            prefix : str, optional
                Prefix for nested items, by default ""

            Returns
            -------
            List[Dict]
                List of dictionaries containing file/directory information
            """
            items = []
            for item in path.iterdir():
                if item.name == ".git":
                    continue
                    
                items.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(item.relative_to(repo_dir))
                })
                
                if item.is_dir():
                    items.extend(get_directory_structure(item, prefix + "  "))
            return items
        
        structure = get_directory_structure(repo_dir)
        
        return {
            'commits': commits,
            'branches': branches,
            'structure': structure,
            'active_branch': repo.active_branch.name,
            'remotes': [r.name for r in repo.remotes]
        }
    except Exception as e:
        raise Exception(f"Failed to analyze repository: {str(e)}")

@mcp.tool()
def execute_git_command(repo_url: str, command: List[str]) -> Dict:
    """
    Execute a Git command in the repository directory.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository.
    command : List[str]
        Command to execute as a list of strings. Must start with 'git'.

    Returns
    -------
    Dict
        Dictionary containing:
        - status: str, Command execution status
        - stdout: str, Command standard output
        - stderr: str, Command standard error

    Raises
    ------
    Exception
        If repository is not found or command execution fails.
    ValueError
        If command doesn't start with 'git'.

    Notes
    -----
    Only git commands are allowed for security reasons.
    Commands are executed in the repository's directory.
    """
    repo_dir = get_repo_dir(repo_url)
    if not repo_dir.exists():
        raise Exception("Repository not found. Clone it first.")
    
    try:
        if not command[0] == "git":
            raise ValueError("Only git commands are allowed")
            
        result = subprocess.run(
            command,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            'status': 'success',
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e.stderr}")

@mcp.tool()
def read_file(repo_url: str, file_path: str) -> str:
    """
    Read content of a file from the repository.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository.
    file_path : str
        Path to the file within the repository.

    Returns
    -------
    str
        Content of the file.

    Raises
    ------
    Exception
        If repository is not found or file reading fails.
    FileNotFoundError
        If the specified file doesn't exist.
    """
    repo_dir = get_repo_dir(repo_url)
    if not repo_dir.exists():
        raise Exception("Repository not found. Clone it first.")
    
    try:
        full_path = repo_dir / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        return full_path.read_text()
    except Exception as e:
        raise Exception(f"Failed to read file: {str(e)}")

@mcp.tool()
def write_file(
    repo_url: str,
    file_path: str,
    content: str,
    commit_message: str = None
) -> Dict:
    """
    Write content to a file and optionally commit changes.

    Parameters
    ----------
    repo_url : str
        The URL of the Git repository.
    file_path : str
        Path where to write the file within the repository.
    content : str
        Content to write to the file.
    commit_message : str, optional
        If provided, changes will be committed with this message.

    Returns
    -------
    Dict
        Dictionary containing:
        - status: str, Operation status
        - path: str, Path to the written file
        - committed: bool, Whether changes were committed
        - commit_hash: str, Hash of the commit (if committed)

    Raises
    ------
    Exception
        If repository is not found or file writing fails.

    Notes
    -----
    If commit_message is provided, changes will be automatically
    committed to the repository. Parent directories will be
    created if they don't exist.
    """
    repo_dir = get_repo_dir(repo_url)
    if not repo_dir.exists():
        raise Exception("Repository not found. Clone it first.")
    
    try:
        full_path = repo_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content)
        
        if commit_message:
            repo = Repo(repo_dir)
            repo.index.add([file_path])
            commit = repo.index.commit(commit_message)
            
            return {
                'status': 'success',
                'path': file_path,
                'committed': True,
                'commit_hash': commit.hexsha
            }
        
        return {
            'status': 'success',
            'path': file_path,
            'committed': False
        }
    except Exception as e:
        raise Exception(f"Failed to write file: {str(e)}")


if __name__ == "__main__":
    mcp.run(transport="stdio")