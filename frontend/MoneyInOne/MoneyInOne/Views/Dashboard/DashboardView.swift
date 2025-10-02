//
//  DashboardView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Main dashboard view displaying portfolio summary and insights
struct DashboardView: View {
    // MARK: - Properties
    
    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: DashboardViewModel
    @Environment(\.scenePhase) private var scenePhase
    
    // MARK: - Initialization
    
    init() {
        _viewModel = State(initialValue: DashboardViewModel())
    }
    
    // MARK: - Body
    
    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.portfolioSummary == nil {
                    loadingView
                } else if let errorMessage = viewModel.errorMessage, viewModel.portfolioSummary == nil {
                    errorView(message: errorMessage)
                } else if viewModel.isEmpty {
                    emptyStateView
                } else if let summary = viewModel.portfolioSummary {
                    contentView(summary: summary)
                }
            }
            .navigationTitle("Dashboard")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    CurrencyPickerMenu()
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    refreshButton
                }
            }
            .onAppear {
                // Load portfolio data
                Task {
                    await viewModel.loadPortfolio(
                        deviceId: coordinator.deviceID,
                        baseCurrency: coordinator.baseCurrency.rawValue
                    )
                }
            }
            .onChange(of: scenePhase) { _, newPhase in
                // Reload when app becomes active
                if newPhase == .active && viewModel.portfolioSummary != nil {
                    Task {
                        await viewModel.loadPortfolio(
                            deviceId: coordinator.deviceID,
                            baseCurrency: coordinator.baseCurrency.rawValue
                        )
                    }
                }
            }
            .onChange(of: coordinator.baseCurrency) { _, newCurrency in
                // Reload portfolio when currency changes
                print("💱 DashboardView: Currency changed to \(newCurrency.rawValue), reloading portfolio...")
                Task {
                    await viewModel.loadPortfolio(
                        deviceId: coordinator.deviceID,
                        baseCurrency: newCurrency.rawValue
                    )
                }
            }
        }
    }
    
    // MARK: - Loading View
    
    private var loadingView: some View {
        LoadingView(message: "Loading your portfolio...")
    }
    
    // MARK: - Error View
    
    private func errorView(message: String) -> some View {
        ErrorView(
            error: APIError.serverError(500, message),
            retryAction: {
                viewModel.retryLoad(
                    deviceId: coordinator.deviceID,
                    baseCurrency: coordinator.baseCurrency.rawValue
                )
            }
        )
    }
    
    // MARK: - Empty State View
    
    private var emptyStateView: some View {
        EmptyStateView(
            icon: "chart.pie",
            title: "Start Your Financial Journey",
            message: "Add your first asset or credit to see your portfolio overview here."
        )
    }
    
    // MARK: - Content View
    
    private func contentView(summary: PortfolioSummary) -> some View {
        ScrollView {
            VStack(spacing: 20) {
                // Portfolio Summary Card
                PortfolioSummaryCard(summary: summary)
                
                // Category Breakdown Chart
                CategoryBreakdownView(summary: summary)
                
                // Top Assets List
                TopAssetsListView(
                    assets: viewModel.topAssets,
                    baseCurrency: summary.baseCurrency,
                    onViewAll: {
                        // TODO: Navigate to Assets tab
                        print("📱 Navigate to Assets tab")
                    }
                )
            }
            .padding()
        }
        .refreshable {
            await viewModel.refresh(
                deviceId: coordinator.deviceID,
                baseCurrency: coordinator.baseCurrency.rawValue
            )
        }
    }
    
    // MARK: - Refresh Button
    
    private var refreshButton: some View {
        Button(action: {
            Task {
                await viewModel.refresh(
                    deviceId: coordinator.deviceID,
                    baseCurrency: coordinator.baseCurrency.rawValue
                )
            }
        }) {
            Image(systemName: "arrow.clockwise")
                .foregroundColor(.primaryColor)
        }
        .disabled(viewModel.isRefreshing || viewModel.isLoading)
    }
}

// MARK: - Preview

#Preview("With Data") {
    let coordinator = AppCoordinator()
    
    DashboardView()
        .environment(coordinator)
}

#Preview("Loading") {
    let coordinator = AppCoordinator()
    
    DashboardView()
        .environment(coordinator)
}


