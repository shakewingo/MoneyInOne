//
//  MoneyInOneApp.swift
//  MoneyInOne
//
//  Created by Ying Yao on 2025/10/1.
//

import SwiftUI

@main
struct MoneyInOneApp: App {
    // MARK: - Properties
    
    @State private var coordinator = AppCoordinator()
    
    // MARK: - Body
    
    var body: some Scene {
        WindowGroup {
            MainTabView()
                .environment(coordinator)
        }
    }
}
