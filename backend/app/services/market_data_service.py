"""Market data service for real-time price fetching and caching using Alpha Vantage API."""

import asyncio
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import aiohttp
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching and caching real-time market data using Alpha Vantage."""

    def __init__(self):
        """Initialize the market data service."""
        self.redis_client: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_connections()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_connections()

    async def _init_connections(self):
        """Initialize Redis and HTTP connections."""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Proceeding without cache.")
            self.redis_client = None

        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.alpha_vantage_timeout)
        )

    async def _close_connections(self):
        """Close all connections."""
        if self.redis_client:
            await self.redis_client.close()
        if self.session:
            await self.session.close()

    async def _get_cached_price(self, key: str) -> Optional[Decimal]:
        """Get cached price from Redis."""
        if not self.redis_client:
            return None
        try:
            cached = await self.redis_client.get(key)
            return Decimal(cached.decode()) if cached else None
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None

    async def _set_cached_price(self, key: str, price: Decimal, ttl: int):
        """Cache price in Redis with TTL."""
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, ttl, str(price))
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")

    async def _call_alpha_vantage(self, params: Dict[str, str]) -> Optional[Dict]:
        """
        Make API call to Alpha Vantage with error handling.

        Args:
            params: API parameters including function, symbol, and apikey

        Returns:
            JSON response data, or None if failed
        """
        if not self.session:
            return None

        try:
            async with self.session.get(
                settings.alpha_vantage_base_url, params=params
            ) as response:
                if response.status != 200:
                    logger.warning(
                        f"Alpha Vantage API error: {response.status} for {params.get('function')}"
                    )
                    return None

                data = await response.json()

                # Check for rate limit
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit reached: {data.get('Note')}")
                    return None

                # Check for error messages
                if "Error Message" in data:
                    logger.error(
                        f"Alpha Vantage error for {params.get('symbol', params.get('from_currency'))}: {data.get('Error Message')}"
                    )
                    return None

                return data

        except Exception as e:
            logger.error(f"Error calling Alpha Vantage API: {e}")
            return None

    async def _fetch_stock_price(self, symbol: str) -> Optional[Decimal]:
        """Fetch stock price from Alpha Vantage."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.alpha_vantage_api_key,
        }

        data = await self._call_alpha_vantage(params)
        if not data:
            return None

        quote = data.get("Global Quote", {})
        price_str = quote.get("05. price")

        if price_str:
            price = Decimal(price_str)
            logger.info(f"Fetched stock price for {symbol}: {price}")
            return price

        logger.warning(f"No price data found for {symbol}")
        return None

    async def _fetch_exchange_rate(
        self, from_currency: str, to_currency: str
    ) -> Optional[Decimal]:
        """Fetch exchange rate from Alpha Vantage (also works for crypto and commodities except previous metal)."""
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": settings.alpha_vantage_api_key,
        }

        data = await self._call_alpha_vantage(params)
        if not data:
            return None

        exchange_data = data.get("Realtime Currency Exchange Rate", {})
        rate_str = exchange_data.get("5. Exchange Rate")

        if rate_str:
            rate = Decimal(rate_str)
            logger.info(f"Fetched exchange rate {from_currency}/{to_currency}: {rate}")
            return rate

        logger.warning(f"No exchange rate found for {from_currency}/{to_currency}")
        return None

    async def _get_with_cache(
        self, cache_key: str, fetch_func, *args, ttl: int = None
    ) -> Optional[Decimal]:
        """
        Generic method to get price with caching.

        Args:
            cache_key: Redis cache key
            fetch_func: Async function to fetch data if not cached
            *args: Arguments to pass to fetch_func
            ttl: Cache TTL in seconds (defaults to market prices TTL)

        Returns:
            Price as Decimal, or None if failed
        """
        # Try cache first
        cached_price = await self._get_cached_price(cache_key)
        if cached_price:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_price

        # Fetch from API
        price = await fetch_func(*args)
        if price:
            ttl = ttl or settings.cache_ttl_market_prices
            await self._set_cached_price(cache_key, price, ttl)

        return price

    async def get_stock_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get stock price with caching.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            Current stock price as Decimal, or None if failed
        """
        return await self._get_with_cache(
            f"stock_price:{symbol}", self._fetch_stock_price, symbol
        )

    async def get_crypto_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get crypto price in USD with caching.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')

        Returns:
            Current crypto price in USD as Decimal, or None if failed
        """
        return await self._get_with_cache(
            f"crypto_price:{symbol}", self._fetch_exchange_rate, symbol, "USD"
        )

    async def get_commodity_price(self, commodity: str) -> Optional[Decimal]:
        """
        Get commodity price (gold, silver) in USD with caching.

        Alpha Vantage treats precious metals as currencies:
        - Gold: XAU
        - Silver: XAG

        Args:
            commodity: Commodity name ('gold' or 'silver')

        Returns:
            Current commodity price in USD per troy ounce as Decimal, or None if failed
        """
        commodity_symbols = {"gold": "XAU", "silver": "XAG"}

        symbol = commodity_symbols.get(commodity.lower())
        if not symbol:
            logger.warning(f"Unsupported commodity: {commodity}")
            return None

        return await self._get_with_cache(
            f"commodity_price:{commodity}", self._fetch_exchange_rate, symbol, "USD"
        )

    async def get_exchange_rate(
        self, from_currency: str, to_currency: str
    ) -> Optional[Decimal]:
        """
        Get exchange rate between currencies with caching.

        Args:
            from_currency: Source currency code (e.g., 'EUR', 'CNY')
            to_currency: Target currency code (e.g., 'USD')

        Returns:
            Exchange rate as Decimal, or None if failed
        """
        if from_currency == to_currency:
            return Decimal("1.0")

        return await self._get_with_cache(
            f"exchange_rate:{from_currency}_{to_currency}",
            self._fetch_exchange_rate,
            from_currency,
            to_currency,
            ttl=settings.cache_ttl_exchange_rates,
        )

    async def update_asset_price(
        self, asset_data: Dict, base_currency: str = "USD"
    ) -> Tuple[bool, Optional[Decimal], Optional[Decimal]]:
        """
        Update single asset price and return (success, market_price, current_amount).

        Args:
            asset_data: Dict with keys: category, symbol, shares, currency, amount
            base_currency: Target currency for conversion (default: USD)
        Returns:
            Tuple of (success, market_price, current_amount)
        """
        category = asset_data.get("category")
        symbol = asset_data.get("symbol")
        shares = asset_data.get("shares", 1)
        currency = asset_data.get("currency")

        if not symbol:
            return False, None, None

        # Fetch market price based on asset category
        price_fetchers = {
            "stock": self.get_stock_price,
            "crypto": self.get_crypto_price,
            "gold": self.get_stock_price,
            "silver": self.get_stock_price,
        }

        fetch_func = price_fetchers.get(category)
        if not fetch_func:
            logger.warning(f"Unsupported asset category: {category}")
            return False, None, None

        market_price = await fetch_func(symbol)
        if not market_price:
            return False, None, None

        # Calculate current amount
        current_amount = market_price * Decimal(str(shares))

        # TODO: potential bug, if currency is CAD but stock's currentcy is USD and base_currency is CNY, need 2 times conversion
        if currency != base_currency:
            exchange_rate = await self.get_exchange_rate(currency, base_currency)
            if exchange_rate:
                current_amount = current_amount * exchange_rate
            else:
                logger.warning(f"Failed to convert {currency} to {base_currency}")

        return True, market_price, current_amount

    async def update_multiple_assets(
        self, assets_data: List[Dict], base_currency: str = "USD"
    ) -> Dict[str, Tuple[bool, Optional[Decimal], Optional[Decimal]]]:
        """
        Update multiple assets concurrently.

        Args:
            assets_data: List of asset dicts with keys: id, category, symbol, shares, currency
            base_currency: Target currency for conversion (default: USD)
        Returns:
            Dict mapping asset_id to (success, market_price, current_amount) tuples
        """
        tasks = [self.update_asset_price(asset_data, base_currency) for asset_data in assets_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to asset IDs
        return {
            asset_data.get("id"): (
                (False, None, None)
                if isinstance(result, Exception)
                else result
            )
            for asset_data, result in zip(assets_data, results)
        }
