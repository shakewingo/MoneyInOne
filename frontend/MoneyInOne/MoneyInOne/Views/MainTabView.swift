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
        TabView(selection: $selectedTab) {
            // Dashboard Tab
            DashboardPlaceholder()
                .tabItem {
                    Label("Dashboard", systemImage: "chart.pie.fill")
                }
                .tag(0)
            
            // Assets Tab
            AssetsPlaceholder()
                .tabItem {
                    Label("Assets", systemImage: "wallet.pass.fill")
                }
                .tag(1)
            
            // Credits Tab
            CreditsPlaceholder()
                .tabItem {
                    Label("Credits", systemImage: "creditcard.fill")
                }
                .tag(2)
        }
        .tint(.primaryColor)
    }
}

// MARK: - Placeholder Views (will be replaced in subsequent phases)

struct DashboardPlaceholder: View {
    @Environment(AppCoordinator.self) private var coordinator
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Image(systemName: "chart.pie.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.primaryColor)
                
                Text("Dashboard")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Coming in Phase 1")
                    .font(.body)
                    .foregroundColor(.gray500)
                
                VStack(alignment: .leading, spacing: 8) {
                    InfoRow(label: "Device ID", value: coordinator.deviceID)
                    InfoRow(label: "Base Currency", value: coordinator.baseCurrency.displayText)
                    InfoRow(label: "Status", value: "✅ Connected")
                }
                .padding()
                .background(Color.gray100)
                .cornerRadius(12)
                .padding(.horizontal)
            }
            .navigationTitle("Dashboard")
        }
    }
}

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

