//
//  MainTabView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Main tab view for app navigation
struct MainTabView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var selectedTab = 0
    
    var body: some View {
        Group {
            if !coordinator.hasCompletedOnboarding {
                OnboardingView()
            } else {
                tabView
            }
        }
    }
    
    private var tabView: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem { Label("Dashboard", systemImage: "chart.pie.fill") }
                .tag(0)
            
            AssetListView()
                .tabItem { Label("Assets", systemImage: "wallet.pass.fill") }
                .tag(1)
            
            CreditListView()
                .tabItem { Label("Credits", systemImage: "creditcard.fill") }
                .tag(2)
        }
        .tint(.primaryColor)
    }
}

// MARK: - Preview

#Preview {
    MainTabView()
        .environment(AppCoordinator())
}

