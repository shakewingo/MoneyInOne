//
//  AssetListViewModel.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation
import Observation

/// View model for managing asset list state and operations
@Observable
class AssetListViewModel {
    // MARK: - Properties
    
    /// Grouped assets by category
    var groupedAssets: [String: AssetCategoryBreakdown] = [:]
    
    /// Loading state
    var isLoading: Bool = false
    
    /// Error message
    var errorMessage: String?
    
    /// Selected asset for navigation
    var selectedAsset: Asset?
    
    // MARK: - Computed Properties
    
    /// Sorted categories for display
    var sortedCategories: [AssetCategory] {
        let categories = groupedAssets.keys.compactMap { AssetCategory(rawValue: $0) }
        return categories.sorted { $0.displayName < $1.displayName }
    }
    
    /// Check if assets list is empty
    var isEmpty: Bool {
        groupedAssets.values.allSatisfy { $0.assets.isEmpty }
    }
    
    /// Total assets count
    var totalCount: Int {
        groupedAssets.values.reduce(0) { $0 + $1.count }
    }
    
    // MARK: - Services
    
    private let assetService: AssetService
    
    // MARK: - Initialization
    
    init(assetService: AssetService = .shared) {
        self.assetService = assetService
    }
    
    // MARK: - Public Methods
    
    /// Loads assets from backend
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func loadAssets(deviceId: String, baseCurrency: String) {
        guard !isLoading else { return }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                print("📋 AssetListViewModel: Loading assets...")
                let assets = try await assetService.fetchGroupedAssets(
                    deviceId: deviceId,
                    baseCurrency: baseCurrency
                )
                
                await MainActor.run {
                    self.groupedAssets = assets
                    self.isLoading = false
                    print("✅ AssetListViewModel: Loaded \(self.totalCount) assets in \(assets.count) categories")
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    self.errorMessage = error.localizedDescription
                    print("❌ AssetListViewModel: Failed to load assets: \(error)")
                }
            }
        }
    }
    
    /// Refreshes asset data
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func refresh(deviceId: String, baseCurrency: String) async {
        print("🔄 AssetListViewModel: Refreshing assets...")
        errorMessage = nil
        
        do {
            let assets = try await assetService.fetchGroupedAssets(
                deviceId: deviceId,
                baseCurrency: baseCurrency
            )
            
            await MainActor.run {
                self.groupedAssets = assets
                print("✅ AssetListViewModel: Refreshed successfully")
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                print("❌ AssetListViewModel: Refresh failed: \(error)")
            }
        }
    }
    
    /// Deletes an asset
    ///
    /// - Parameters:
    ///   - assetId: Asset ID to delete
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func deleteAsset(assetId: UUID, deviceId: String, baseCurrency: String) async {
        print("🗑️ AssetListViewModel: Deleting asset \(assetId)...")
        
        do {
            try await assetService.deleteAsset(assetId: assetId, deviceId: deviceId)
            print("✅ AssetListViewModel: Asset deleted, reloading list...")
            
            // Reload assets after deletion
            await refresh(deviceId: deviceId, baseCurrency: baseCurrency)
        } catch {
            await MainActor.run {
                self.errorMessage = "Failed to delete asset: \(error.localizedDescription)"
                print("❌ AssetListViewModel: Delete failed: \(error)")
            }
        }
    }
    
    /// Retries loading assets after an error
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for conversion
    func retryLoad(deviceId: String, baseCurrency: String) {
        print("🔄 AssetListViewModel: Retrying load...")
        loadAssets(deviceId: deviceId, baseCurrency: baseCurrency)
    }
    
    /// Gets assets for a specific category
    ///
    /// - Parameter category: Asset category
    /// - Returns: Array of assets in that category
    func assets(for category: AssetCategory) -> [Asset] {
        return groupedAssets[category.rawValue]?.assets ?? []
    }
    
    /// Gets count for a specific category
    ///
    /// - Parameter category: Asset category
    /// - Returns: Count of assets in that category
    func count(for category: AssetCategory) -> Int {
        return groupedAssets[category.rawValue]?.count ?? 0
    }
}

