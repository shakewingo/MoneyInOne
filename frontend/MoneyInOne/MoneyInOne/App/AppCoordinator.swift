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
    var deviceID: String
    var baseCurrency: Currency = .CNY
    var isInitialized = false
    var initializationError: Error?
    var hasCompletedOnboarding = false  // NEW
    var hasAnyData = false  // NEW
    
    init() {
        self.deviceID = DeviceIDManager.shared.getDeviceID()
        
        // Check if user has completed onboarding
        self.hasCompletedOnboarding = UserDefaults.standard.bool(forKey: "hasCompletedOnboarding")
        
        // Load saved currency
        if let savedCurrency = UserDefaults.standard.string(forKey: "baseCurrency"),
           let currency = Currency(rawValue: savedCurrency) {
            self.baseCurrency = currency
        }
    }
    
    func markOnboardingComplete() {
        hasCompletedOnboarding = true
        UserDefaults.standard.set(true, forKey: "hasCompletedOnboarding")
    }
    
    func updateBaseCurrency(_ currency: Currency) {
        baseCurrency = currency
        UserDefaults.standard.set(currency.rawValue, forKey: "baseCurrency")
        print("💰 Base currency updated to: \(currency.rawValue)")
    }
    
}
