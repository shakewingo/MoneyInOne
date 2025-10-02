//
//  AssetService.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation

/// Service for asset-related CRUD operations
class AssetService {
    // MARK: - Properties
    
    static let shared = AssetService()
    private let apiService: APIService
    
    // MARK: - Initialization
    
    private init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    // MARK: - Asset Operations
    
    /// Fetches grouped assets by category from backend
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for amount conversion
    /// - Returns: Dictionary of asset category breakdowns
    /// - Throws: APIError if request fails
    func fetchGroupedAssets(
        deviceId: String,
        baseCurrency: String
    ) async throws -> [String: AssetCategoryBreakdown] {
        print("📦 AssetService: Fetching grouped assets for device: \(deviceId), currency: \(baseCurrency)")
        
        let queryItems = [
            URLQueryItem(name: "device_id", value: deviceId),
            URLQueryItem(name: "base_currency", value: baseCurrency)
        ]
        
        do {
            let grouped: [String: AssetCategoryBreakdown] = try await apiService.get(
                endpoint: "/assets",
                queryItems: queryItems
            )
            print("✅ AssetService: Fetched \(grouped.count) asset categories")
            return grouped
        } catch {
            print("❌ AssetService: Failed to fetch grouped assets: \(error)")
            throw error
        }
    }
    
    /// Creates a new asset
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - asset: Asset creation request data
    /// - Returns: Created asset with server-generated fields
    /// - Throws: APIError if request fails
    func createAsset(
        deviceId: String,
        asset: AssetCreate
    ) async throws -> Asset {
        print("➕ AssetService: Creating asset '\(asset.name)' for device: \(deviceId)")
        
        // Validate stock-specific fields
        if asset.category == .stock || asset.category == .crypto {
            guard asset.symbol != nil, !asset.symbol!.isEmpty else {
                throw APIError.validationError("Symbol is required for stock and crypto assets")
            }
            guard asset.shares != nil, asset.shares! > 0 else {
                throw APIError.validationError("Shares must be greater than 0 for stock and crypto assets")
            }
        }
        
        let headers = ["X-Device-ID": deviceId]
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            // Backend returns wrapped response: {"message": "...", "data": {...}}
            let response: APIResponse<Asset> = try await apiService.post(
                endpoint: "/assets",
                body: asset,
                queryItems: queryItems,
                headers: headers
            )
            print("✅ AssetService: Asset created successfully")
            guard let createdAsset = response.data else {
                throw APIError.missingData
            }
            return createdAsset
        } catch {
            print("❌ AssetService: Failed to create asset: \(error)")
            throw error
        }
    }
    
    /// Updates an existing asset
    ///
    /// - Parameters:
    ///   - assetId: Asset UUID to update
    ///   - deviceId: User device identifier
    ///   - update: Asset update request data
    /// - Returns: Updated asset
    /// - Throws: APIError if request fails
    func updateAsset(
        assetId: UUID,
        deviceId: String,
        update: AssetUpdate
    ) async throws -> Asset {
        print("✏️ AssetService: Updating asset \(assetId) for device: \(deviceId)")
        
        // Validate stock-specific fields if category is being updated to stock/crypto
        if let category = update.category, (category == .stock || category == .crypto) {
            if let symbol = update.symbol, symbol.isEmpty {
                throw APIError.validationError("Symbol cannot be empty for stock and crypto assets")
            }
            if let shares = update.shares, shares <= 0 {
                throw APIError.validationError("Shares must be greater than 0")
            }
        }
        
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            // Backend returns wrapped response: {"message": "...", "data": {...}}
            let response: APIResponse<Asset> = try await apiService.put(
                endpoint: "/assets/\(assetId.uuidString)",
                body: update,
                queryItems: queryItems
            )
            print("✅ AssetService: Asset updated successfully")
            guard let updatedAsset = response.data else {
                throw APIError.missingData
            }
            return updatedAsset
        } catch {
            print("❌ AssetService: Failed to update asset: \(error)")
            throw error
        }
    }
    
    /// Deletes an asset
    ///
    /// - Parameters:
    ///   - assetId: Asset UUID to delete
    ///   - deviceId: User device identifier
    /// - Throws: APIError if request fails
    func deleteAsset(
        assetId: UUID,
        deviceId: String
    ) async throws {
        print("🗑️ AssetService: Deleting asset \(assetId) for device: \(deviceId)")
        
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            let _: SuccessResponse = try await apiService.delete(
                endpoint: "/assets/\(assetId.uuidString)",
                queryItems: queryItems
            )
            print("✅ AssetService: Asset deleted successfully")
        } catch {
            print("❌ AssetService: Failed to delete asset: \(error)")
            throw error
        }
    }
}

/// Extended APIError for validation errors
extension APIError {
    static func validationError(_ message: String) -> APIError {
        return .decodingError(NSError(domain: "ValidationError", code: 400, userInfo: [NSLocalizedDescriptionKey: message]))
    }
}

