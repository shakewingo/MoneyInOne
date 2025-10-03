//
//  CurrencyFormatter.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Handles currency formatting and display
struct CurrencyFormatter {
    // MARK: - Currency Symbols
    
    private static let currencySymbols: [String: String] = [
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "$",
        "AUD": "$"
    ]
    
    // MARK: - Decimal Places
    
    private static let decimalPlaces: [String: Int] = [
        "CNY": 2,
        "USD": 2,
        "EUR": 2,
        "GBP": 2,
        "JPY": 0,  // Japanese Yen has no decimal places
        "CAD": 2,
        "AUD": 2
    ]
    
    // MARK: - Public Methods
    
    /// Formats a decimal amount with currency symbol
    ///
    /// - Parameters:
    ///   - amount: The amount to format
    ///   - currency: The currency code (e.g., "USD", "CNY")
    ///   - showSymbol: Whether to show the currency symbol
    /// - Returns: Formatted string (e.g., "¥1,234.56" or "1,234.56 CNY")
    static func format(amount: Decimal, currency: String, showSymbol: Bool = true) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = 0  // Show integers only
        formatter.minimumFractionDigits = 0  // Show integers only
        formatter.groupingSeparator = ","
        formatter.decimalSeparator = "."
        
        let formattedNumber = formatter.string(from: NSDecimalNumber(decimal: amount)) ?? "0"
        
        if showSymbol, let symbol = currencySymbols[currency] {
            return "\(symbol)\(formattedNumber)"
        } else {
            return "\(formattedNumber) \(currency)"
        }
    }
    
    /// Gets the currency symbol for a given currency code
    ///
    /// - Parameter currency: The currency code
    /// - Returns: The currency symbol or the code if not found
    static func symbol(for currency: String) -> String {
        return currencySymbols[currency] ?? currency
    }
    
    /// Gets the number of decimal places for a currency
    ///
    /// - Parameter currency: The currency code
    /// - Returns: The number of decimal places
    static func decimalPlaces(for currency: String) -> Int {
        return decimalPlaces[currency] ?? 2
    }
}

