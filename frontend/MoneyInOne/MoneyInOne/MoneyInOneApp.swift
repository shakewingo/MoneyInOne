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
            Group {
                if coordinator.isInitialized {
                    // Main app content
                    MainTabView()
                        .environment(coordinator)
                } else if let error = coordinator.initializationError {
                    // Show error if initialization failed
                    ErrorView(error: error) {
                        Task {
                            await coordinator.initialize()
                        }
                    }
                } else {
                    // Show loading during initialization
                    LoadingView(message: "Initializing MoneyInOne...")
                }
            }
            .task {
                // Initialize app on launch
                if !coordinator.isInitialized {
                    await coordinator.initialize()
                }
            }
        }
    }
}
