//
//  DeviceIDManager.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation
import Security

/// Manages device ID storage and retrieval using Keychain for secure persistence
final class DeviceIDManager {
    // MARK: - Properties
    
    static let shared = DeviceIDManager()
    
    private let service = "com.moneyinone.app"
    private let account = "device_id"
    
    // MARK: - Initialization
    
    private init() {}
    
    // MARK: - Public Methods
    
    /// Gets the device ID, generating and storing one if it doesn't exist
    ///
    /// - Returns: The device ID string
    func getDeviceID() -> String {
        // Try to retrieve existing device ID
        if let existingID = retrieveFromKeychain() {
            return existingID
        }
        
        // Generate new device ID if none exists
        let newID = UUID().uuidString
        saveToKeychain(newID)
        return newID
    }
    
    /// Resets the device ID (generates a new one)
    /// Use with caution as this will create a new user profile on backend
    func resetDeviceID() -> String {
        deleteFromKeychain()
        let newID = UUID().uuidString
        saveToKeychain(newID)
        return newID
    }
    
    // MARK: - Private Methods
    
    private func saveToKeychain(_ value: String) {
        guard let data = value.data(using: .utf8) else { return }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
        ]
        
        // Delete any existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status != errSecSuccess {
            print("⚠️ DeviceIDManager: Failed to save to Keychain with status: \(status)")
        } else {
            print("✅ DeviceIDManager: Successfully saved device ID to Keychain")
        }
    }
    
    private func retrieveFromKeychain() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let deviceID = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        print("✅ DeviceIDManager: Retrieved device ID from Keychain")
        return deviceID
    }
    
    private func deleteFromKeychain() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        
        SecItemDelete(query as CFDictionary)
        print("🗑️ DeviceIDManager: Deleted device ID from Keychain")
    }
}

