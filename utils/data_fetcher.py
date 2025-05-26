import requests
import time
from typing import List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
COINGECKO_API = "https://api.coingecko.com/api/v3"
REQUEST_DELAY = 1.5  # Delay between requests to respect API rate limits

# --- PASTE YOUR COINGECKO API KEY HERE ---
# It's recommended to load this from an environment variable (e.g., os.getenv("COINGECKO_API_KEY"))
# For direct pasting, replace "YOUR_COINGECKO_API_KEY_HERE" with your actual key.
COINGECKO_API_KEY = "CG-1TyXWQgHQvTgrPzY7pPKtT67"

def test_api_connection():
    """Test if API key works with simple endpoint"""
    try:
        logger.info("Testing API connection...")
        url = f"{COINGECKO_API}/simple/price"
        params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
        
        # Try different header formats
        header_formats = [
            {'x-cg-demo-api-key': COINGECKO_API_KEY},
            {'X-Cg-Demo-Api-Key': COINGECKO_API_KEY},
            {'x-cg-demo-api-key': COINGECKO_API_KEY.strip()},
        ]
        
        for i, headers in enumerate(header_formats):
            logger.info(f"Testing header format {i+1}: {list(headers.keys())[0]}")
            response = requests.get(url, params=params, headers=headers)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"✅ API key works with header format {i+1}!")
                logger.info(f"Response: {response.json()}")
                return headers
            else:
                logger.warning(f"❌ Header format {i+1} failed: {response.text[:200]}")
        
        # Try without headers (free tier)
        logger.info("Testing free tier (no API key)...")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logger.info("✅ Free tier works!")
            return None
        else:
            logger.error(f"❌ Free tier also failed: {response.text[:200]}")
            
    except Exception as e:
        logger.error(f"API test error: {e}")
        
    return False

def get_crypto_data(crypto_id: str, days: int = 30) -> List[float]:
    """
    Fetches historical hourly price data from CoinGecko API.
    
    Args:
        crypto_id (str): CoinGecko cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
        days (int): Number of days of data to fetch.
        
    Returns:
        List[float]: A list of hourly prices, with the most recent price at the end.
    
    Raises:
        requests.exceptions.RequestException: If the API request fails (e.g., network error, 4xx/5xx status).
        KeyError, ValueError: If data parsing fails or insufficient data is received.
    """
    try:
        logger.info(f"Fetching data for {crypto_id} (last {days} days)")
        
        url = f"{COINGECKO_API}/coins/{crypto_id}/market_chart"
        
        # Ensure days is within the range that provides hourly data automatically
        # CoinGecko provides hourly data for 2-90 days without needing interval parameter
        if days < 2:
            days = 2
            logger.info(f"Adjusted days to {days} to get hourly data")
        elif days > 90:
            days = 90
            logger.info(f"Adjusted days to {days} to stay within hourly data range")
        
        params = {
            'vs_currency': 'usd',
            'days': days
            # Removed 'interval': 'hourly' - this is automatic for 2-90 days
        }
        
        # Log request details
        logger.info(f"Making request to: {url}")
        logger.info(f"With params: {params}")
        logger.info(f"API Key (first 10 chars): {COINGECKO_API_KEY[:10]}...")
        
        # Try different header formats
        header_formats = [
            {'x-cg-demo-api-key': COINGECKO_API_KEY},
            {'X-Cg-Demo-Api-Key': COINGECKO_API_KEY},
            {'x-cg-demo-api-key': COINGECKO_API_KEY.strip()},
            {'x-cg-pro-api-key': COINGECKO_API_KEY},  # In case it's actually a pro key
        ]
        
        response = None
        successful_headers = None
        
        for i, headers in enumerate(header_formats):
            logger.info(f"Trying header format {i+1}: {list(headers.keys())[0]}")
            try:
                response = requests.get(url, params=params, headers=headers)
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"✅ Success with header format {i+1}!")
                    successful_headers = headers
                    break
                elif response.status_code == 401:
                    logger.warning(f"❌ Header format {i+1} failed with 401 Unauthorized")
                elif response.status_code == 429:
                    logger.warning(f"❌ Header format {i+1} failed with 429 Rate Limited")
                else:
                    logger.warning(f"❌ Header format {i+1} failed with status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"❌ Header format {i+1} failed with exception: {e}")
                continue
        
        # If all header formats failed, try without API key (free tier with limitations)
        if response is None or response.status_code != 200:
            logger.warning("All API key formats failed. Trying free tier (limited requests)...")
            try:
                # For free tier, use smaller days value to be safe
                free_params = params.copy()
                if days > 7:
                    free_params['days'] = 7
                    logger.info("Reduced days to 7 for free tier compatibility")
                
                response = requests.get(url, params=free_params)
                logger.info(f"Free tier response status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ Free tier request successful!")
                    params = free_params  # Use the adjusted params
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Free tier request also failed: {e}")
        
        # Final check and error handling
        if response is None:
            raise requests.exceptions.RequestException("All API request attempts failed")
            
        # Log response details for debugging
        if response.status_code != 200:
            logger.error(f"Final response status: {response.status_code}")
            logger.error(f"Response headers: {dict(response.headers)}")
            logger.error(f"Response body: {response.text[:500]}")
            
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        
        # Parse the response
        data = response.json()
        
        if 'prices' not in data:
            logger.error(f"No 'prices' key in response. Available keys: {list(data.keys())}")
            raise KeyError("'prices' key not found in API response")
            
        prices = [point[1] for point in data['prices']]
        
        if not prices:
            logger.warning(f"No price data found for {crypto_id}. Returned empty list.")
            return []
        
        logger.info(f"Successfully fetched {len(prices)} data points for {crypto_id}")
        logger.info(f"Price range: ${min(prices):,.2f} - ${max(prices):,.2f}")
        logger.info(f"Latest price: ${prices[-1]:,.2f}")
        
        return prices
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {crypto_id}: {str(e)}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing failed for {crypto_id}: {str(e)}. Response: {response.text if 'response' in locals() else 'N/A'}")
        raise
    finally:
        # Apply rate limiting delay
        logger.info(f"Applying {REQUEST_DELAY}s delay for rate limiting...")
        time.sleep(REQUEST_DELAY)

# Test function to verify API setup
if __name__ == "__main__":
    logger.info("Running API connection test...")
    test_result = test_api_connection()
    
    if test_result:
        logger.info("API connection test passed. Testing data fetching...")
        try:
            prices = get_crypto_data("bitcoin", days=7)
            logger.info(f"✅ Data fetching test successful! Got {len(prices)} prices")
        except Exception as e:
            logger.error(f"❌ Data fetching test failed: {e}")
    else:
        logger.error("❌ API connection test failed")