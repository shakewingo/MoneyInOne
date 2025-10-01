//
//  MetadataService.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// Response structure for metadata endpoint
struct MetadataResponse: Codable {
    let currencies: [CurrencyInfo]
    let assetCategories: [String]
    let creditCategories: [String]
    
    enum CodingKeys: String, CodingKey {
        case currencies
        case assetCategories = "asset_categories"
        case creditCategories = "credit_categories"
    }
}

/// Service for fetching application metadata
class MetadataService {
    // MARK: - Properties
    
    static let shared = MetadataService()
    
    private let apiService = APIService.shared
    
    // MARK: - Initialization
    
    private init() {}
    
    // MARK: - Public Methods
    
    /// Fetches all metadata (currencies and categories)
    ///
    /// - Returns: MetadataResponse containing all metadata
    func fetchMetadata() async throws -> MetadataResponse {
        return try await apiService.get(endpoint: "/metadata")
    }
    
    /// Fetches list of supported currencies
    ///
    /// - Returns: Array of CurrencyInfo
    func fetchCurrencies() async throws -> [CurrencyInfo] {
        return try await apiService.get(endpoint: "/metadata/currencies")
    }
    
    /// Fetches list of asset categories
    ///
    /// - Returns: Array of category strings
    func fetchAssetCategories() async throws -> [String] {
        return try await apiService.get(endpoint: "/metadata/asset-categories")
    }
    
    /// Fetches list of credit categories
    ///
    /// - Returns: Array of category strings
    func fetchCreditCategories() async throws -> [String] {
        return try await apiService.get(endpoint: "/metadata/credit-categories")
    }
}

