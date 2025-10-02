//
//  AddEditViewModel.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation
import Observation

/// View model for managing Add/Edit form state and operations
@Observable
class AddEditViewModel {
    // MARK: - Properties
    
    let mode: FormMode
    
    // Form fields
    var name: String = ""
    var selectedAssetCategory: AssetCategory = .cash
    var selectedCreditCategory: CreditCategory = .creditCard
    var amount: String = ""
    var currency: Currency = .CNY
    var date: Date = Date()
    var notes: String = ""
    var symbol: String = ""
    var shares: String = ""
    var isMarketTracked: Bool = true  // Default to true for stock/crypto
    
    // State
    var isLoading: Bool = false
    var errorMessage: String?
    var validationErrors: [String: String] = [:]
    
    // MARK: - Services
    
    private let assetService: AssetService
    private let creditService: CreditService
    
    // MARK: - Computed Properties
    
    /// Whether stock-specific fields are required
    var requiresStockFields: Bool {
        guard mode.isAssetMode else { return false }
        return selectedAssetCategory == .stock || selectedAssetCategory == .crypto
    }
    
    /// Whether this is an asset form
    var isAssetMode: Bool {
        mode.isAssetMode
    }
    
    /// Date label based on mode
    var dateLabel: String {
        mode.isAssetMode ? "Purchase Date" : "Issue Date"
    }
    
    // MARK: - Initialization
    
    init(
        mode: FormMode,
        assetService: AssetService = .shared,
        creditService: CreditService = .shared
    ) {
        self.mode = mode
        self.assetService = assetService
        self.creditService = creditService
        
        // Pre-populate fields in edit mode
        if let asset = mode.editingAsset {
            self.name = asset.name
            self.selectedAssetCategory = asset.category
            self.amount = String(describing: asset.amount)
            self.currency = Currency(rawValue: asset.currency) ?? .CNY
            self.date = asset.purchaseDate
            self.notes = asset.notes ?? ""
            self.symbol = asset.symbol ?? ""
            self.shares = asset.shares.map { String(describing: $0) } ?? ""
            self.isMarketTracked = asset.isMarketTracked
        } else if let credit = mode.editingCredit {
            self.name = credit.name
            self.selectedCreditCategory = credit.category
            self.amount = String(describing: credit.amount)
            self.currency = Currency(rawValue: credit.currency) ?? .CNY
            self.date = credit.issueDate
            self.notes = credit.notes ?? ""
        }
    }
    
    // MARK: - Validation
    
    /// Validates all form fields
    ///
    /// - Returns: True if all fields are valid
    func validateForm() -> Bool {
        validationErrors.removeAll()
        
        // Name validation
        if name.trimmingCharacters(in: .whitespaces).isEmpty {
            validationErrors["name"] = "Name is required"
        }
        
        // Amount validation
        guard let amountValue = Decimal(string: amount.trimmingCharacters(in: .whitespaces)) else {
            validationErrors["amount"] = "Please enter a valid amount"
            return false
        }
        
        if amountValue <= 0 {
            validationErrors["amount"] = "Amount must be greater than 0"
        }
        
        // Stock-specific validation
        if requiresStockFields {
            let trimmedSymbol = symbol.trimmingCharacters(in: .whitespaces)
            if trimmedSymbol.isEmpty {
                validationErrors["symbol"] = "Symbol is required for stocks and crypto"
            }
            
            guard let sharesValue = Double(shares.trimmingCharacters(in: .whitespaces)) else {
                validationErrors["shares"] = "Please enter a valid number of shares"
                return false
            }
            
            if sharesValue <= 0 {
                validationErrors["shares"] = "Shares must be greater than 0"
            }
        }
        
        return validationErrors.isEmpty
    }
    
    // MARK: - Helpers
    
    /// Normalizes a date to midnight (00:00:00) in UTC timezone
    /// This ensures the backend receives dates with zero time component
    private func normalizeDate(_ date: Date) -> Date {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(identifier: "UTC") ?? TimeZone.current
        let components = calendar.dateComponents([.year, .month, .day], from: date)
        return calendar.date(from: components) ?? date
    }
    
    // MARK: - Form Submission
    
    /// Submits the form (create or update)
    ///
    /// - Parameter deviceId: User device identifier
    /// - Throws: APIError if submission fails
    func submitForm(deviceId: String) async throws {
        guard validateForm() else {
            throw APIError.validationError("Please fix the validation errors")
        }
        
        isLoading = true
        errorMessage = nil
        
        defer {
            Task { @MainActor in
                self.isLoading = false
            }
        }
        
        do {
            if mode.isAssetMode {
                try await submitAsset(deviceId: deviceId)
            } else {
                try await submitCredit(deviceId: deviceId)
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
            }
            throw error
        }
    }
    
    /// Submits asset form
    private func submitAsset(deviceId: String) async throws {
        guard let amountValue = Decimal(string: amount) else {
            throw APIError.validationError("Invalid amount")
        }
        
        if mode.isEditMode, let asset = mode.editingAsset {
            // Update existing asset
            let update = AssetUpdate(
                name: name.trimmingCharacters(in: .whitespaces),
                category: selectedAssetCategory,
                amount: amountValue,
                currency: currency.rawValue,
                purchaseDate: normalizeDate(date),
                notes: notes.isEmpty ? nil : notes,
                symbol: requiresStockFields ? symbol : nil,
                shares: requiresStockFields ? Double(shares) : nil,
                isMarketTracked: requiresStockFields ? isMarketTracked : nil,
                currentAmount: nil,
                originalAmount: nil
            )
            
            _ = try await assetService.updateAsset(
                assetId: asset.id,
                deviceId: deviceId,
                update: update
            )
        } else {
            // Create new asset
            let create = AssetCreate(
                name: name.trimmingCharacters(in: .whitespaces),
                category: selectedAssetCategory,
                amount: amountValue,
                currency: currency.rawValue,
                purchaseDate: normalizeDate(date),
                notes: notes.isEmpty ? nil : notes,
                symbol: requiresStockFields ? symbol : nil,
                shares: requiresStockFields ? Double(shares) : nil,
                isMarketTracked: requiresStockFields ? isMarketTracked : nil
            )
            
            _ = try await assetService.createAsset(
                deviceId: deviceId,
                asset: create
            )
        }
    }
    
    /// Submits credit form
    private func submitCredit(deviceId: String) async throws {
        guard let amountValue = Decimal(string: amount) else {
            throw APIError.validationError("Invalid amount")
        }
        
        if mode.isEditMode, let credit = mode.editingCredit {
            // Update existing credit
            let update = CreditUpdate(
                name: name.trimmingCharacters(in: .whitespaces),
                category: selectedCreditCategory,
                amount: amountValue,
                currency: currency.rawValue,
                issueDate: normalizeDate(date),
                notes: notes.isEmpty ? nil : notes
            )
            
            _ = try await creditService.updateCredit(
                creditId: credit.id,
                deviceId: deviceId,
                update: update
            )
        } else {
            // Create new credit
            let create = CreditCreate(
                name: name.trimmingCharacters(in: .whitespaces),
                category: selectedCreditCategory,
                amount: amountValue,
                currency: currency.rawValue,
                issueDate: normalizeDate(date),
                notes: notes.isEmpty ? nil : notes
            )
            
            _ = try await creditService.createCredit(
                deviceId: deviceId,
                credit: create
            )
        }
    }
    
    // MARK: - Delete
    
    /// Deletes the item being edited
    ///
    /// - Parameter deviceId: User device identifier
    /// - Throws: APIError if deletion fails
    func deleteItem(deviceId: String) async throws {
        guard mode.isEditMode else {
            throw APIError.validationError("Cannot delete in add mode")
        }
        
        isLoading = true
        errorMessage = nil
        
        defer {
            Task { @MainActor in
                self.isLoading = false
            }
        }
        
        do {
            if let asset = mode.editingAsset {
                try await assetService.deleteAsset(assetId: asset.id, deviceId: deviceId)
            } else if let credit = mode.editingCredit {
                try await creditService.deleteCredit(creditId: credit.id, deviceId: deviceId)
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
            }
            throw error
        }
    }
}

