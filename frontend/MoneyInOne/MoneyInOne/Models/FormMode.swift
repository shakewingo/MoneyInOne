//
//  FormMode.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation

/// Represents the different modes for the Add/Edit form
enum FormMode: Identifiable {
    case addAsset
    case editAsset(Asset)
    case addCredit
    case editCredit(Credit)
    
    // MARK: - Identifiable
    
    var id: String {
        switch self {
        case .addAsset:
            return "addAsset"
        case .editAsset(let asset):
            return "editAsset-\(asset.id.uuidString)"
        case .addCredit:
            return "addCredit"
        case .editCredit(let credit):
            return "editCredit-\(credit.id.uuidString)"
        }
    }
    
    // MARK: - Computed Properties
    
    /// Whether this is an edit mode (vs add mode)
    var isEditMode: Bool {
        switch self {
        case .editAsset, .editCredit:
            return true
        default:
            return false
        }
    }
    
    /// Whether this is for an asset (vs credit)
    var isAssetMode: Bool {
        switch self {
        case .addAsset, .editAsset:
            return true
        default:
            return false
        }
    }
    
    /// Title for the form
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
    
    /// Button title for save action
    var saveButtonTitle: String {
        switch self {
        case .addAsset:
            return "Add Asset"
        case .editAsset:
            return "Update Asset"
        case .addCredit:
            return "Add Credit"
        case .editCredit:
            return "Update Credit"
        }
    }
    
    /// Get the asset being edited (if in edit asset mode)
    var editingAsset: Asset? {
        if case .editAsset(let asset) = self {
            return asset
        }
        return nil
    }
    
    /// Get the credit being edited (if in edit credit mode)
    var editingCredit: Credit? {
        if case .editCredit(let credit) = self {
            return credit
        }
        return nil
    }
}

