//
//  Credit.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation
import SwiftUI

/// Credit categories
enum CreditCategory: String, Codable, CaseIterable, Identifiable {
    case creditCard = "credit_card"
    case loan = "loan"
    case mortgage = "mortgage"
    case lineOfCredit = "line_of_credit"
    case other = "other"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .creditCard: return "Credit Card"
        case .loan: return "Loan"
        case .mortgage: return "Mortgage"
        case .lineOfCredit: return "Line of Credit"
        case .other: return "Other"
        }
    }
    
    var iconName: String {
        switch self {
        case .creditCard: return "creditcard.fill"
        case .loan: return "banknote.fill"
        case .mortgage: return "house.and.flag.fill"
        case .lineOfCredit: return "arrow.left.arrow.right"
        case .other: return "ellipsis.circle"
        }
    }
    
    var color: Color {
        switch self {
        case .creditCard: return Color(hex: "EF4444")   // Red
        case .loan: return Color(hex: "F97316")         // Orange
        case .mortgage: return Color(hex: "F472B6")     // Rose Pink
        case .lineOfCredit: return Color(hex: "FBBF24") // Yellow
        case .other: return Color(hex: "A855F7")        // Purple (vibrant, not grey!)
        }
    }
}

/// Credit model matching backend schema
struct Credit: Identifiable, Codable {
    let id: UUID
    let userId: UUID
    var name: String
    var category: CreditCategory
    var amount: Decimal
    var currency: String
    var issueDate: Date
    var notes: String?
    var convertedAmount: Decimal?
    var conversionRate: Decimal?
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, name, category, amount, currency, notes
        case userId = "user_id"
        case issueDate = "issue_date"
        case convertedAmount = "converted_amount"
        case conversionRate = "conversion_rate"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

/// Request model for creating a credit
struct CreditCreate: Codable {
    let name: String
    let category: CreditCategory
    let amount: Decimal
    let currency: String
    let issueDate: Date
    let notes: String?
    
    enum CodingKeys: String, CodingKey {
        case name, category, amount, currency, notes
        case issueDate = "issue_date"
    }
}

/// Request model for updating a credit
struct CreditUpdate: Codable {
    let name: String?
    let category: CreditCategory?
    let amount: Decimal?
    let currency: String?
    let issueDate: Date?
    let notes: String?
    
    enum CodingKeys: String, CodingKey {
        case name, category, amount, currency, notes
        case issueDate = "issue_date"
    }
}

/// Credit category breakdown response
struct CreditCategoryBreakdown: Codable {
    let credits: [Credit]
    let totalAmount: Decimal
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case credits
        case totalAmount = "total_amount"
        case count
    }
}

