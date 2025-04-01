# MCP GitLab Integration

This module provides a FastMCP server implementation for Git repository operations, including cloning, analysis, and file manipulation. It is designed to work with GitLab repositories and supports both public and private repositories.

## Features

- **Repository Cloning**: Clone repositories with optional token-based authentication.
- **Repository Analysis**: Analyze repository structure, branches, commits, and remotes.
- **Git Command Execution**: Execute custom Git commands securely within the repository.
- **File Operations**: Read and write files in the repository with optional commit support.

## Configuration

The module uses environment variables for configuration:

- `GITLAB_TOKEN`: Personal access token for GitLab (required for private repositories).
- `GITLAB_URL`: Base URL of the GitLab instance (default: `https://gitlab.com`).
- `TEMP_DIR`: Directory for storing cloned repositories (default: system temp directory).

## Running the Example Agent

The `example_agent.py` script demonstrates how to use the MCP tools for GitLab repository analysis. Follow these steps to run the agent:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the `mcp_gitlab` directory with the following content:
   ```properties
   GITLAB_URL=https://gitlab.com
   GITLAB_TOKEN="ENTER_YOUR_GITLAB_TOKEN_HERE"
   ```

3. **Run the Example Agent**:
   Execute the `example_agent.py` script:
   ```bash
   python example_agent.py
   ```

4. **Interact with the Agent**:
   - Type your queries to interact with the agent.
   - Example queries:
     - "Clone the repository at `https://gitlab.com/username/repo.git`."
     - "Analyze the repository structure and list all files."
     - "Read the file `README.md` from the repository."

5. **Exit the Agent**:
   Type `exit`, `quit`, or `bye` to end the session.

## Tools

The following tools are exposed via the FastMCP server:

1. **`clone_repository`**: Clone or update a Git repository.
2. **`analyze_repository`**: Perform a comprehensive analysis of a repository.
3. **`execute_git_command`**: Execute custom Git commands in the repository.
4. **`read_file`**: Read the content of a file from the repository.
5. **`write_file`**: Write content to a file and optionally commit changes.

## License

This project is licensed under the MIT License.