//
//  PortfolioService.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Service for portfolio-related operations
class PortfolioService {
    // MARK: - Properties
    
    static let shared = PortfolioService()
    private let apiService: APIService
    
    // MARK: - Initialization
    
    private init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    // MARK: - Portfolio Operations
    
    /// Fetches portfolio summary from backend
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for calculations
    /// - Returns: Portfolio summary with all amounts in base currency
    /// - Throws: APIError if request fails
    func fetchPortfolioSummary(
        deviceId: String,
        baseCurrency: String
    ) async throws -> PortfolioSummary {
        print("📊 Fetching portfolio summary for device: \(deviceId), currency: \(baseCurrency)")
        
        let queryItems = [
            URLQueryItem(name: "device_id", value: deviceId),
            URLQueryItem(name: "base_currency", value: baseCurrency)
        ]
        
        do {
            let summary: PortfolioSummary = try await apiService.get(
                endpoint: "/portfolio/summary",
                queryItems: queryItems
            )
            print("✅ Portfolio summary fetched successfully")
            return summary
        } catch {
            print("❌ Failed to fetch portfolio summary: \(error)")
            throw error
        }
    }
    
    /// Fetches grouped assets by category
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
        print("📦 Fetching grouped assets for device: \(deviceId)")
        
        let queryItems = [
            URLQueryItem(name: "device_id", value: deviceId),
            URLQueryItem(name: "base_currency", value: baseCurrency)
        ]
        
        do {
            let grouped: [String: AssetCategoryBreakdown] = try await apiService.get(
                endpoint: "/assets/",
                queryItems: queryItems
            )
            print("✅ Grouped assets fetched successfully")
            return grouped
        } catch {
            print("❌ Failed to fetch grouped assets: \(error)")
            throw error
        }
    }
    
    /// Refreshes market prices for all tracked assets
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for price conversions
    /// - Returns: Success response with refresh statistics
    /// - Throws: APIError if request fails
    func refreshMarketPrices(
        deviceId: String,
        baseCurrency: String
    ) async throws -> SuccessResponse {
        print("🔄 Refreshing market prices for device: \(deviceId), currency: \(baseCurrency)")
        
        let headers = ["X-Device-ID": deviceId]
        let queryItems = [URLQueryItem(name: "base_currency", value: baseCurrency)]
        
        do {
            let response: SuccessResponse = try await apiService.post(
                endpoint: "/assets/refresh-prices",
                queryItems: queryItems,
                headers: headers
            )
            print("✅ Market prices refreshed: \(response.message)")
            return response
        } catch {
            print("❌ Failed to refresh market prices: \(error)")
            throw error
        }
    }
    
    /// Refreshes market price for a single asset
    ///
    /// - Parameters:
    ///   - assetId: Asset UUID
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for price conversions
    /// - Returns: Success response
    /// - Throws: APIError if request fails
    func refreshSingleAssetPrice(
        assetId: UUID,
        deviceId: String,
        baseCurrency: String
    ) async throws -> SuccessResponse {
        print("🔄 Refreshing price for asset: \(assetId), currency: \(baseCurrency)")
        
        let headers = ["X-Device-ID": deviceId]
        let queryItems = [URLQueryItem(name: "base_currency", value: baseCurrency)]
        
        do {
            let response: SuccessResponse = try await apiService.post(
                endpoint: "/assets/\(assetId.uuidString)/refresh-price",
                queryItems: queryItems,
                headers: headers
            )
            print("✅ Asset price refreshed: \(response.message)")
            return response
        } catch {
            print("❌ Failed to refresh asset price: \(error)")
            throw error
        }
    }
}

