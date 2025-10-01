//
//  Currency.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Supported currencies in the app
enum Currency: String, Codable, CaseIterable, Identifiable {
    case CNY = "CNY"  // Chinese Yuan (Primary)
    case USD = "USD"  // US Dollar
    case EUR = "EUR"  // Euro
    case GBP = "GBP"  // British Pound
    case JPY = "JPY"  // Japanese Yen
    case CAD = "CAD"  // Canadian Dollar
    case AUD = "AUD"  // Australian Dollar
    
    var id: String { rawValue }
    
    /// Full currency name
    var name: String {
        switch self {
        case .CNY: return "Chinese Yuan"
        case .USD: return "US Dollar"
        case .EUR: return "Euro"
        case .GBP: return "British Pound"
        case .JPY: return "Japanese Yen"
        case .CAD: return "Canadian Dollar"
        case .AUD: return "Australian Dollar"
        }
    }
    
    /// Currency symbol
    var symbol: String {
        CurrencyFormatter.symbol(for: rawValue)
    }
    
    /// Display text combining code and name
    var displayText: String {
        "\(rawValue)"
    }
}

/// Currency information from API
struct CurrencyInfo: Codable, Identifiable {
    let code: String
    let name: String
    let symbol: String
    
    var id: String { code }
    
    var displayText: String {
        "\(code) - \(name)"
    }
}

