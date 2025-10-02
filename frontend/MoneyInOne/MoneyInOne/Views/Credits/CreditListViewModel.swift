//
//  CreditListViewModel.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation
import Observation

/// View model for managing credit list state and operations
@Observable
class CreditListViewModel {
    // MARK: - Properties
    
    /// Grouped credits by category
    var groupedCredits: [String: CreditCategoryBreakdown] = [:]
    
    /// Loading state
    var isLoading: Bool = false
    
    /// Error message
    var errorMessage: String?
    
    /// Selected credit for navigation
    var selectedCredit: Credit?
    
    // MARK: - Computed Properties
    
    /// Sorted categories for display
    var sortedCategories: [CreditCategory] {
        let categories = groupedCredits.keys.compactMap { CreditCategory(rawValue: $0) }
        return categories.sorted { $0.displayName < $1.displayName }
    }
    
    /// Check if credits list is empty
    var isEmpty: Bool {
        groupedCredits.values.allSatisfy { $0.credits.isEmpty }
    }
    
    /// Total credits count
    var totalCount: Int {
        groupedCredits.values.reduce(0) { $0 + $1.count }
    }
    
    // MARK: - Services
    
    private let creditService: CreditService
    
    // MARK: - Initialization
    
    init(creditService: CreditService = .shared) {
        self.creditService = creditService
    }
    
    // MARK: - Public Methods
    
    /// Loads credits from backend
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func loadCredits(deviceId: String, baseCurrency: String) {
        guard !isLoading else { return }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                print("💳 CreditListViewModel: Loading credits...")
                let credits = try await creditService.fetchGroupedCredits(
                    deviceId: deviceId,
                    baseCurrency: baseCurrency
                )
                
                await MainActor.run {
                    self.groupedCredits = credits
                    self.isLoading = false
                    print("✅ CreditListViewModel: Loaded \(self.totalCount) credits in \(credits.count) categories")
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    self.errorMessage = error.localizedDescription
                    print("❌ CreditListViewModel: Failed to load credits: \(error)")
                }
            }
        }
    }
    
    /// Refreshes credit data
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func refresh(deviceId: String, baseCurrency: String) async {
        print("🔄 CreditListViewModel: Refreshing credits...")
        errorMessage = nil
        
        do {
            let credits = try await creditService.fetchGroupedCredits(
                deviceId: deviceId,
                baseCurrency: baseCurrency
            )
            
            await MainActor.run {
                self.groupedCredits = credits
                print("✅ CreditListViewModel: Refreshed successfully")
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                print("❌ CreditListViewModel: Refresh failed: \(error)")
            }
        }
    }
    
    /// Deletes a credit
    ///
    /// - Parameters:
    ///   - creditId: Credit ID to delete
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func deleteCredit(creditId: UUID, deviceId: String, baseCurrency: String) async {
        print("🗑️ CreditListViewModel: Deleting credit \(creditId)...")
        
        do {
            try await creditService.deleteCredit(creditId: creditId, deviceId: deviceId)
            print("✅ CreditListViewModel: Credit deleted, reloading list...")
            
            // Reload credits after deletion
            await refresh(deviceId: deviceId, baseCurrency: baseCurrency)
        } catch {
            await MainActor.run {
                self.errorMessage = "Failed to delete credit: \(error.localizedDescription)"
                print("❌ CreditListViewModel: Delete failed: \(error)")
            }
        }
    }
    
    /// Retries loading credits after an error
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func retryLoad(deviceId: String, baseCurrency: String) {
        print("🔄 CreditListViewModel: Retrying load...")
        loadCredits(deviceId: deviceId, baseCurrency: baseCurrency)
    }
    
    /// Gets credits for a specific category
    ///
    /// - Parameter category: Credit category
    /// - Returns: Array of credits in that category
    func credits(for category: CreditCategory) -> [Credit] {
        return groupedCredits[category.rawValue]?.credits ?? []
    }
    
    /// Gets count for a specific category
    ///
    /// - Parameter category: Credit category
    /// - Returns: Count of credits in that category
    func count(for category: CreditCategory) -> Int {
        return groupedCredits[category.rawValue]?.count ?? 0
    }
}

