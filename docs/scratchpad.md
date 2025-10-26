## Background and Motivation

Currency conversion bugs appear when switching between different chosen base currencies. Root causes identified:
- Converted values are being persisted (e.g., `amount` overwritten during refresh), leading to double conversions later.
- Conversion is performed in multiple places (price refresh and aggregation), violating single-source-of-truth for conversion.
- The order-of-operations requirement (use `symbol * shares * market_price` when available, else fallback to `original_amount`) is not consistently applied in portfolio/asset aggregations.
- Caching is available (Redis) but conversion pipeline does not reliably leverage cached quotes and exchange rates per chosen currency.

Success here improves correctness, predictability, and performance of cross-currency portfolio views, especially dashboard totals and breakdowns.

## Key Challenges and Analysis

- Data semantics drift: `Asset.amount` is currently being set to a converted value during refresh. This conflicts with its original meaning (user-entered amount in original currency) and causes incorrect results when the base currency changes later.
- Conversion duplication: `MarketDataService.update_asset_price` both fetches market data and converts to base currency. Conversion also happens again in `FinanceService` during summaries.
- Consistent source-of-truth: We need one place where conversion happens for request-time chosen currency, using cached data.
- Order-of-operations: For market-tracked assets with `symbol` and `shares`, dashboard must use `shares * market_price (asset currency) * FX(asset_currency -> base_currency)`. Otherwise, fallback to `original_amount`.
- UX contract: Dashboard requires conversion; Assets/Credits pages should primarily show original-currency values, but may include a separate converted field when explicitly requested.
- Performance: Minimize external calls; rely on Redis cached prices and FX with proper TTLs. Avoid persisting base-currency-specific numbers in DB.

## High-Level Task Breakdown

1) Refactor price refresh to avoid persistence of converted amounts
- Remove base-currency conversion from `MarketDataService.update_asset_price` and `update_multiple_assets`.
- In `FinanceService.refresh_prices`:
  - Do NOT overwrite `Asset.amount` with converted values.
  - Only update `current_amount` in the asset's native/original currency and `last_price_update`.
  - Initialize `original_amount` if missing, leave it immutable afterwards.
- Success criteria: After refresh, `amount` remains original; `current_amount` reflects latest market value in original currency; no base-currency data is stored.

2) Centralize conversion in `FinanceService` at request time
- Introduce a helper: `compute_native_amount(item)`:
  - If `symbol` and `shares` exist: fetch cached market price for the symbol (USD for stock/crypto/precious metals per current API usage) and compute `shares * market_price` as native amount.
  - Else: use `original_amount` if available, else `amount`.
- Update `_group_and_convert_items` and `_calculate_category_summary` to:
  - Use `compute_native_amount`.
  - Convert once via `_convert_to_base_currency(native_amount, item.currency, base_currency)`.
  - Populate `converted_amount` and `conversion_rate` on responses.
- Success criteria: Dashboard totals change correctly when `base_currency` changes; no double conversions; logic follows order-of-operations.

3) Ensure asset category-specific price fetchers are correct and cached
- Reuse `MarketDataService.get_stock_price`, `get_crypto_price`, `get_commodity_price` (XAU/XAG) which already cache.
- Ensure exchange rates are fetched once and cached per currency pair using `get_exchange_rate`.
- Success criteria: Minimal external API calls when switching base currencies within TTL.

4) Clarify Assets/Credits endpoints behavior
- Keep existing grouped endpoints returning both original fields and `converted_amount` when `base_currency` is provided.
- Ensure the primary amount fields (`amount`, `current_amount`) remain in original currency, matching frontend expectations for details pages.
- Success criteria: Assets/Credits screens show original-currency values; any displayed conversion uses `converted_amount` explicitly.

5) Data model consistency and safety guards
- Add internal guardrails to prevent future code from overwriting `amount` with base-currency values in refresh paths.
- Add logging around conversion paths (from/to currencies, used rate) to ease debugging.
- Success criteria: No writes to `amount` during refresh in code review and tests; logs confirm single conversion path.

6) Tests and validations
- Unit tests for `compute_native_amount` and conversion logic (including fallback path).
- Integration tests for portfolio summary across multiple `base_currency` values with cached data.
- Regression tests ensuring refresh does not mutate `amount` and only updates `current_amount`.
- Success criteria: 90%+ coverage for changed logic; all tests pass; amounts stable across currency switches.

## Project Status Board

- [ ] 1) Refactor refresh to avoid persisted conversions
- [ ] 2) Centralize conversion in FinanceService at request time
- [ ] 3) Ensure price and FX cache usage is consistent
- [ ] 4) Clarify Assets/Credits endpoints behavior (original vs converted fields)
- [ ] 5) Add safety guards and logging
- [ ] 6) Add unit/integration tests and regression tests

## Current Status / Progress Tracking

- Planning completed. Awaiting approval to proceed with implementation.

## Executor Feedback or Help Requests

- Confirm whether Assets/Credits list views should include converted values or strictly original-currency only. Current frontend requests a `base_currency` for assets; plan keeps both original and `converted_amount` fields to serve both needs without breaking.
