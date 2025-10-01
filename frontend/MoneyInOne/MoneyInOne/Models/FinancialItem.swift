//
//  FinancialItem.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Protocol for shared behavior between Assets and Credits
protocol FinancialItem: Identifiable {
    var id: UUID { get }
    var name: String { get }
    var amount: Decimal { get }
    var currency: String { get }
    var notes: String? { get }
    var convertedAmount: Decimal? { get }
    var conversionRate: Decimal? { get }
    var createdAt: Date { get }
    var updatedAt: Date { get }
}

/// Mode for add/edit view to determine which type and operation
enum FinancialItemMode {
    case addAsset
    case editAsset(Asset)
    case addCredit
    case editCredit(Credit)
    
    var isAsset: Bool {
        switch self {
        case .addAsset, .editAsset:
            return true
        case .addCredit, .editCredit:
            return false
        }
    }
    
    var isEdit: Bool {
        switch self {
        case .editAsset, .editCredit:
            return true
        case .addAsset, .addCredit:
            return false
        }
    }
    
    var title: String {
        switch self {
        case .addAsset:
            return "Add Asset"
        case .editAsset:
            return "Edit Asset"
        case .addCredit:
            return "Add Credit"
        case .editCredit:
            return "Edit Credit"
        }
    }
}

