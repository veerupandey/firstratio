import asyncio
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
import dotenv
dotenv.load_dotenv()

async def create_gitlab_agent(session):
    """Create and configure a GitLab tools agent with MCP tools."""
    # Initialize the MCP toolkit
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()

    # Create an agent with the MCP toolkit
    return Agent(
        model=AzureOpenAI(id="gpt-4o-mini"),
        tools=[mcp_tools],
        add_history_to_messages=True,
        num_history_responses=5,
        instructions=dedent("""\
            You are a GitLab repository analysis assistant that helps users explore, analyze, and modify GitLab repositories.
            
            CAPABILITIES:
            1. Repository Access and Analysis:
               - Clone repositories using clone_repository (requires repo URL)
               - Analyze repository structure and history with analyze_repository
               - Execute git commands using execute_git_command
               - Read and write files using read_file and write_file
            
            AUTHENTICATION:
            - For private repositories, ensure GITLAB_TOKEN is configured in .env file
            - Use token authentication when accessing private repositories
            
            WORKFLOW:
            1. Always start by cloning the repository to temporary directory
            2. Perform requested analysis or modifications
            3. Provide clear, formatted output of findings
            4. Handle errors gracefully and provide clear error messages
            
            GUIDELINES:
            - Verify repository URL is provided before operations
            - Use markdown formatting for structured output
            - Present analysis results in a clear, organized manner
            - For file modifications, always explain the changes being made
            - When executing git commands, ensure they are safe and valid
            
            LIMITATIONS:
            - Can only execute git-related shell commands
            - Temporary files are stored in system temp directory
            - Some operations may require authentication
            
            ERROR HANDLING:
            - If repository not found: Request valid repository URL
            - If authentication fails: Verify GITLAB_TOKEN in .env
            - If file not found: Confirm correct file path
            
            Always maintain context of the conversation and provide clear, actionable responses. If needed, read few important files to answer.
            Format complex output using markdown for better readability.
            """),
        markdown=True,
        show_tool_calls=True,
    )


async def run_agent():
    """Run an interactive loop that continuously asks for user input."""
    print("Welcome to the GitLab Analysis Assistant!")
    print("Type 'exit', 'quit', or 'bye' to end the session.")
    print("----------------------------------------------------")
    
    # Initialize the MCP server and agent once, outside the loop
    server_params = StdioServerParameters(
        command="python",
        args=["gitlab_mcp.py"],  
    )

    # Create a client session to connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Create the agent once
            agent = await create_gitlab_agent(session)
            
            while True:
                # Get user input
                user_input = input("\n\nWhat would you like to ask? > ")
                
                # Check if user wants to exit
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("Goodbye!")
                    break
                    
                # Skip empty inputs
                if not user_input.strip():
                    continue
                    
                try:
                    # Use the existing agent instead of creating a new one
                    print("\nProcessing your request...")
                    await agent.aprint_response(user_input, stream=True)
                except Exception as e:
                    print(f"\nAn error occurred: {str(e)}")
                    print("Please try again with a different query.")
            
# Example usage
if __name__ == "__main__":
    asyncio.run(run_agent())