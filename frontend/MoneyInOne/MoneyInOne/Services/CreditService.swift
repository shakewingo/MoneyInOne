//
//  CreditService.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import Foundation

/// Service for credit-related CRUD operations
class CreditService {
    // MARK: - Properties
    
    static let shared = CreditService()
    private let apiService: APIService
    
    // MARK: - Initialization
    
    private init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    // MARK: - Credit Operations
    
    /// Fetches grouped credits by category from backend
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - baseCurrency: Base currency for amount conversion
    /// - Returns: Dictionary of credit category breakdowns
    /// - Throws: APIError if request fails
    func fetchGroupedCredits(
        deviceId: String,
        baseCurrency: String
    ) async throws -> [String: CreditCategoryBreakdown] {
        print("💳 CreditService: Fetching grouped credits for device: \(deviceId), currency: \(baseCurrency)")
        
        let queryItems = [
            URLQueryItem(name: "device_id", value: deviceId),
            URLQueryItem(name: "base_currency", value: baseCurrency)
        ]
        
        do {
            let grouped: [String: CreditCategoryBreakdown] = try await apiService.get(
                endpoint: "/credits",
                queryItems: queryItems
            )
            print("✅ CreditService: Fetched \(grouped.count) credit categories")
            return grouped
        } catch {
            print("❌ CreditService: Failed to fetch grouped credits: \(error)")
            throw error
        }
    }
    
    /// Creates a new credit
    ///
    /// - Parameters:
    ///   - deviceId: User device identifier
    ///   - credit: Credit creation request data
    /// - Returns: Created credit with server-generated fields
    /// - Throws: APIError if request fails
    func createCredit(
        deviceId: String,
        credit: CreditCreate
    ) async throws -> Credit {
        print("➕ CreditService: Creating credit '\(credit.name)' for device: \(deviceId)")
        
        let headers = ["X-Device-ID": deviceId]
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            // Backend returns wrapped response: {"message": "...", "data": {...}}
            let response: APIResponse<Credit> = try await apiService.post(
                endpoint: "/credits",
                body: credit,
                queryItems: queryItems,
                headers: headers
            )
            print("✅ CreditService: Credit created successfully")
            guard let createdCredit = response.data else {
                throw APIError.missingData
            }
            return createdCredit
        } catch {
            print("❌ CreditService: Failed to create credit: \(error)")
            throw error
        }
    }
    
    /// Updates an existing credit
    ///
    /// - Parameters:
    ///   - creditId: Credit UUID to update
    ///   - deviceId: User device identifier
    ///   - update: Credit update request data
    /// - Returns: Updated credit
    /// - Throws: APIError if request fails
    func updateCredit(
        creditId: UUID,
        deviceId: String,
        update: CreditUpdate
    ) async throws -> Credit {
        print("✏️ CreditService: Updating credit \(creditId) for device: \(deviceId)")
        
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            // Backend returns wrapped response: {"message": "...", "data": {...}}
            let response: APIResponse<Credit> = try await apiService.put(
                endpoint: "/credits/\(creditId.uuidString)",
                body: update,
                queryItems: queryItems
            )
            print("✅ CreditService: Credit updated successfully")
            guard let updatedCredit = response.data else {
                throw APIError.missingData
            }
            return updatedCredit
        } catch {
            print("❌ CreditService: Failed to update credit: \(error)")
            throw error
        }
    }
    
    /// Deletes a credit
    ///
    /// - Parameters:
    ///   - creditId: Credit UUID to delete
    ///   - deviceId: User device identifier
    /// - Throws: APIError if request fails
    func deleteCredit(
        creditId: UUID,
        deviceId: String
    ) async throws {
        print("🗑️ CreditService: Deleting credit \(creditId) for device: \(deviceId)")
        
        let queryItems = [URLQueryItem(name: "device_id", value: deviceId)]
        
        do {
            let _: SuccessResponse = try await apiService.delete(
                endpoint: "/credits/\(creditId.uuidString)",
                queryItems: queryItems
            )
            print("✅ CreditService: Credit deleted successfully")
        } catch {
            print("❌ CreditService: Failed to delete credit: \(error)")
            throw error
        }
    }
}

