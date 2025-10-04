import requests

def test_alpha_vantage(api_key: str, symbol: str = "AAPL"):
    # Alpha Vantage API endpoint for stock quotes
    url = "https://www.alphavantage.co/query"
    
    # Parameters for the API request
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": api_key
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the JSON response
        data = response.json()
        
        # Check if the response contains the expected data
        if "Time Series (5min)" in data:
            print(f"API is working. Retrieved data for {symbol}:")
            # Print the first data point
            first_time, first_data = next(iter(data["Time Series (5min)"].items()))
            print(f"Time: {first_time}, Data: {first_data}")
        else:
            print("API response does not contain expected data. Check your API key and parameters.")
            print("Response:", data)
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Replace 'YOUR_API_KEY' with your actual Alpha Vantage API key
test_alpha_vantage(api_key="MY_API_KEY")