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
            
            AssetsPlaceholder()
                .tabItem { Label("Assets", systemImage: "wallet.pass.fill") }
                .tag(1)
            
            CreditsPlaceholder()
                .tabItem { Label("Credits", systemImage: "creditcard.fill") }
                .tag(2)
        }
        .tint(.primaryColor)
    }
}

// MARK: - Placeholder Views (will be replaced in subsequent phases)

struct AssetsPlaceholder: View {
    var body: some View {
        NavigationStack {
            EmptyStateView(
                icon: "wallet.pass",
                title: "Assets View",
                message: "Assets list will be implemented in Phase 2"
            )
            .navigationTitle("Assets")
        }
    }
}

struct CreditsPlaceholder: View {
    var body: some View {
        NavigationStack {
            EmptyStateView(
                icon: "creditcard",
                title: "Credits View",
                message: "Credits list will be implemented in Phase 2"
            )
            .navigationTitle("Credits")
        }
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.gray600)
            Spacer()
            Text(value)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.gray900)
        }
    }
}

#Preview {
    MainTabView()
        .environment(AppCoordinator())
}

