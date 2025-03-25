import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define server parameters
server_params = StdioServerParameters(
    command="python",
    args=["finance_mcp_server.py"],  # Ensure this points to the correct server script
)

async def run():
    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print('Connected to the server')
            
            # List available tools and display in log
            tools = await session.list_tools()
            print("Available tools:")
            print(tools.tools)

            # Call the financial statements tool
            response = await session.call_tool(
                "get_financial_statements",
                arguments={
                    "ticker": "AAPL",  # Example ticker
                    "statement_type": "income"  # Options: "income", "balance", or "cash"
                }
            )
        return response

if __name__ == "__main__":
    # Run the client and print the response
    from pprint import pprint
    response = asyncio.run(run())
    print("Tool response:")
    pprint(response.content[0].text)