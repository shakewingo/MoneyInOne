//
//  Asset.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation
import SwiftUI

/// Asset categories
enum AssetCategory: String, Codable, CaseIterable, Identifiable {
  case cash = "cash"
  case stock = "stock"
  case crypto = "crypto"
  case realEstate = "real_estate"
  case bond = "bond"
  case gold = "gold"
  case silver = "silver"
  case other = "other"

  var id: String { rawValue }

  var displayName: String {
    switch self {
    case .cash: return "Cash"
    case .stock: return "Stock"
    case .crypto: return "Crypto"
    case .realEstate: return "Real Estate"
    case .bond: return "Bond"
    case .gold: return "Gold"
    case .silver: return "Silver"
    case .other: return "Other"
    }
  }

  var iconName: String {
    switch self {
    case .cash: return "dollarsign.circle"
    case .stock: return "chart.line.uptrend.xyaxis"
    case .crypto: return "bitcoinsign.circle"
    case .realEstate: return "house.fill"
    case .bond: return "doc.text.fill"
    case .gold: return "sparkles"
    case .silver: return "circle.hexagongrid.fill"
    case .other: return "ellipsis.circle"
    }
  }

  var color: Color {
    switch self {
    case .cash: return Color(hex: "10B981")        // Emerald Green
    case .stock: return Color(hex: "3B82F6")       // Sky Blue
    case .crypto: return Color(hex: "F59E0B")      // Amber Orange
    case .realEstate: return Color(hex: "8B5CF6")  // Violet Purple
    case .bond: return Color(hex: "6366F1")        // Indigo Blue
    case .gold: return Color(hex: "FCD34D")        // Golden Yellow
    case .silver: return Color(hex: "06B6D4")      // Cyan (vibrant, not grey!)
    case .other: return Color(hex: "EC4899")       // Pink (vibrant, not grey!)
    }
  }
}

/// Asset model matching backend schema
struct Asset: Identifiable, Codable {
  let id: UUID
  let userId: UUID
  var name: String
  var category: AssetCategory
  var amount: Decimal
  var currency: String
  var purchaseDate: Date
  var notes: String?
  var symbol: String?
  var shares: Double?
  var originalAmount: Decimal?
  var currentAmount: Decimal?
  var lastPriceUpdate: Date?
  var isMarketTracked: Bool
  var convertedAmount: Decimal?
  var conversionRate: Decimal?
  let createdAt: Date
  let updatedAt: Date
  
  /// Computed property that returns currentAmount if available, otherwise falls back to amount
  var displayAmount: Decimal {
    return currentAmount ?? amount
  }

  enum CodingKeys: String, CodingKey {
    case id, name, category, amount, currency, notes, symbol, shares
    case userId = "user_id"
    case purchaseDate = "purchase_date"
    case originalAmount = "original_amount"
    case currentAmount = "current_amount"
    case lastPriceUpdate = "last_price_update"
    case isMarketTracked = "is_market_tracked"
    case convertedAmount = "converted_amount"
    case conversionRate = "conversion_rate"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
  }
}

/// Request model for creating an asset
struct AssetCreate: Codable {
  let name: String
  let category: AssetCategory
  let amount: Decimal
  let currency: String
  let purchaseDate: Date
  let notes: String?
  let symbol: String?
  let shares: Double?
  let isMarketTracked: Bool?

  enum CodingKeys: String, CodingKey {
    case name, category, amount, currency, notes, symbol, shares
    case purchaseDate = "purchase_date"
    case isMarketTracked = "is_market_tracked"
  }
}

/// Request model for updating an asset
struct AssetUpdate: Codable {
  let name: String?
  let category: AssetCategory?
  let amount: Decimal?
  let currency: String?
  let purchaseDate: Date?
  let notes: String?
  let symbol: String?
  let shares: Double?
  let isMarketTracked: Bool?
  let currentAmount: Decimal?
  let originalAmount: Decimal?

  enum CodingKeys: String, CodingKey {
    case name, category, amount, currency, notes, symbol, shares
    case purchaseDate = "purchase_date"
    case isMarketTracked = "is_market_tracked"
    case currentAmount = "current_amount"
    case originalAmount = "original_amount"
  }
}

/// Asset category breakdown response
struct AssetCategoryBreakdown: Codable {
  let assets: [Asset]
  let totalAmount: Decimal
  let count: Int

  enum CodingKeys: String, CodingKey {
    case assets
    case totalAmount = "total_amount"
    case count
  }
}
