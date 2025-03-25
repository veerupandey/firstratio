# MCP Basics with LangChain

This project demonstrates the integration of **MCP (Model Context Protocol)** and it's usage with frameworks like **LangChain** for building AI-powered tools and workflows. It includes examples of financial data retrieval, file system operations, and multi-server MCP setups.

## Features

- **Financial Analysis**: Fetch financial statements (income, balance, cash flow) using `yfinance`.
- **File System Operations**: Perform file and directory operations like reading, writing, and listing contents.
- **LangChain Integration**: Use LangChain to create agents that interact with MCP tools.
- **Multi-Server MCP**: Example of using multiple MCP servers in a single workflow.

## Project Structure

- **`mcp_langchain.ipynb`**: Jupyter notebook demonstrating LangChain and MCP integration.
- **`finance_mcp_server.py`**: MCP server for fetching financial statements.
- **`filesystem_mcp_server.py`**: MCP server for file system operations.
- **`finance_mcp_client.py`**: Client script for interacting with the financial MCP server.
- **`requirements.txt`**: Dependencies required for the project.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Test the finance server using the client:
   ```bash
   python finance_mcp_client.py
   ```

3. Explore the Jupyter notebook:
   ```bash
   mcp_langchain.ipynb
   ```

## LangChain Integration

- Use the `mcp_langchain.ipynb` notebook to interact with MCP tools via LangChain.
- Example questions for LangChain:
  - "What's the revenue in 2024 from the financial income statement for ticker TSLA?"
  - "Get financial income statement for ticker TSLA and write to a file called tsla.json."

## Requirements

- Python 3.8+
- MCP CLI
- LangChain and related adapters
- `yfinance` for financial data

## Usage

- Use the notebook to interact with MCP tools via LangChain.
- Run the client scripts to test finance MCP servers.
