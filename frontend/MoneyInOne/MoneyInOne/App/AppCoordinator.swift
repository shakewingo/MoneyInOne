//
//  AppCoordinator.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation
import SwiftUI

/// Coordinates app initialization and global state
@Observable
class AppCoordinator {
    // MARK: - Properties
    
    /// The device ID used for API authentication
    var deviceID: String
    
    /// Currently selected base currency for display
    var baseCurrency: Currency = .CNY
    
    /// Whether the app has completed initialization
    var isInitialized = false
    
    /// Initialization error if any
    var initializationError: Error?
    
    // MARK: - Initialization
    
    init() {
        // Get or generate device ID
        self.deviceID = DeviceIDManager.shared.getDeviceID()
        
        // Load saved base currency preference
        if let savedCurrency = UserDefaults.standard.string(forKey: "baseCurrency"),
           let currency = Currency(rawValue: savedCurrency) {
            self.baseCurrency = currency
        }
        
        print("✅ AppCoordinator initialized with device ID: \(deviceID)")
        print("💰 Base currency: \(baseCurrency.rawValue)")
    }
    
    // MARK: - Public Methods
    
    /// Performs app initialization tasks
    func initialize() async {
        do {
            // Test API connectivity by fetching metadata
            print("🚀 Initializing app...")
            let metadata = try await MetadataService.shared.fetchMetadata()
            print("✅ Successfully connected to API")
            print("📦 Available currencies: \(metadata.currencies.map { $0.code }.joined(separator: ", "))")
            print("📦 Asset categories: \(metadata.assetCategories.joined(separator: ", "))")
            print("📦 Credit categories: \(metadata.creditCategories.joined(separator: ", "))")
            
            isInitialized = true
            initializationError = nil
        } catch {
            print("❌ Initialization failed: \(error.localizedDescription)")
            initializationError = error
            isInitialized = false
        }
    }
    
    /// Updates the base currency and saves preference
    ///
    /// - Parameter currency: The new base currency
    func updateBaseCurrency(_ currency: Currency) {
        baseCurrency = currency
        UserDefaults.standard.set(currency.rawValue, forKey: "baseCurrency")
        print("💰 Base currency updated to: \(currency.rawValue)")
    }
    
    /// Resets device ID (creates a new user profile)
    func resetDeviceID() {
        deviceID = DeviceIDManager.shared.resetDeviceID()
        print("🔄 Device ID reset to: \(deviceID)")
    }
}

