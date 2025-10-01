//
//  Portfolio.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Asset breakdown in portfolio summary
struct AssetBreakdown: Codable {
    let totalAmount: Decimal
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case totalAmount = "total_amount"
        case count
    }
}

/// Credit breakdown in portfolio summary
struct CreditBreakdown: Codable {
    let totalAmount: Decimal
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case totalAmount = "total_amount"
        case count
    }
}

/// Portfolio summary response from API
struct PortfolioSummary: Codable {
    let baseCurrency: String
    let assetSummary: [String: AssetBreakdown]
    let creditSummary: [String: CreditBreakdown]
    let netWorth: Decimal
    let lastUpdated: Date
    
    enum CodingKeys: String, CodingKey {
        case baseCurrency = "base_currency"
        case assetSummary = "asset_summary"
        case creditSummary = "credit_summary"
        case netWorth = "net_worth"
        case lastUpdated = "last_updated"
    }
    
    /// Total assets across all categories
    var totalAssets: Decimal {
        assetSummary.values.reduce(Decimal.zero) { $0 + $1.totalAmount }
    }
    
    /// Total credits across all categories
    var totalCredits: Decimal {
        creditSummary.values.reduce(Decimal.zero) { $0 + $1.totalAmount }
    }
    
    /// Total number of assets
    var totalAssetCount: Int {
        assetSummary.values.reduce(0) { $0 + $1.count }
    }
    
    /// Total number of credits
    var totalCreditCount: Int {
        creditSummary.values.reduce(0) { $0 + $1.count }
    }
}

