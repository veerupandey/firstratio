from mcp.server.fastmcp import FastMCP
from yfinance import Ticker
import json

# Create a named server
mcp = FastMCP("financial-analysis")

@mcp.tool()
def get_financial_statements(ticker: str, statement_type: str = "income") -> str:
    """
    Fetch financial statements for a given company.

    Args:
        ticker (str): Ticker symbol of the company (e.g., AAPL, GOOGL).
        statement_type (str, optional): Type of financial statement to retrieve 
                                       ("income", "balance", or "cash"). Defaults to "income".

    Returns:
        str: JSON string containing the company's financial statements or an error message.
    """
    # Validate the ticker input
    if not ticker or not isinstance(ticker, str):
        return json.dumps({"error": "Invalid ticker symbol. Please provide a valid string."})

    try:
        # Fetch data from the API
        t = Ticker(ticker)
        
        # Get the appropriate financial statement based on the statement_type
        if statement_type.lower() == "income":
            data = t.financials
            statement_name = "Income Statement"
        elif statement_type.lower() == "balance":
            data = t.balance_sheet
            statement_name = "Balance Sheet"
        elif statement_type.lower() == "cash":
            data = t.cashflow
            statement_name = "Cash Flow Statement"
        else:
            return json.dumps({"error": f"Invalid statement type '{statement_type}'. Use 'income', 'balance', or 'cash'."})

        # Check if data is found and valid
        if data is None or data.empty:
            return json.dumps({"error": f"No {statement_name} found for ticker '{ticker}'."})

        # Convert the index (which may contain Timestamps) to strings
        data.index = data.index.astype(str)
        
        # Convert columns (which may be Timestamps) to strings
        data.columns = data.columns.astype(str)

        # Convert the data to a dictionary for JSON serialization
        financial_data = data.to_dict()

        # Prepare the response
        response = {
            "ticker": ticker,
            "statement_type": statement_name,
            "data": financial_data,
            "message": f"{statement_name} fetched successfully."
        }
        return json.dumps(response, indent=4)

    except Exception as e:
        # Handle any exceptions that occur
        return json.dumps({"error": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    mcp.run(transport="stdio")