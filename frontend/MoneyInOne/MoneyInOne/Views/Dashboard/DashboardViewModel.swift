//
//  DashboardViewModel.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation
import SwiftUI

/// View model for Dashboard view
@Observable
class DashboardViewModel {
  // MARK: - Properties

  /// Current portfolio summary
  var portfolioSummary: PortfolioSummary?

  /// Grouped assets by category
  var groupedAssets: [String: AssetCategoryBreakdown] = [:]

  /// Loading state
  var isLoading = false

  /// Refreshing state (for pull-to-refresh)
  var isRefreshing = false

  /// Error message if any
  var errorMessage: String?

  /// Computed property: is portfolio empty?
  var isEmpty: Bool {
    guard let summary = portfolioSummary else { return true }
    return summary.totalAssetCount == 0 && summary.totalCreditCount == 0
  }

  /// Computed property: top assets sorted by value
  var topAssets: [Asset] {
    let allAssets = groupedAssets.values.flatMap { $0.assets }
    return Array(
      allAssets
        .sorted { ($0.convertedAmount ?? $0.amount) > ($1.convertedAmount ?? $1.amount) }
        .prefix(5))
  }

  // MARK: - Dependencies

  private let portfolioService: PortfolioService

  // MARK: - Initialization

  init(portfolioService: PortfolioService = .shared) {
    self.portfolioService = portfolioService
  }

  // MARK: - Public Methods

  /// Load portfolio data
  func loadPortfolio(deviceId: String, baseCurrency: String) async {
    guard !isLoading else { return }

    isLoading = true
    errorMessage = nil

    print("🔄 DashboardViewModel: Loading portfolio data...")
    print("💰 Using currency: \(baseCurrency)")
    print("📱 Using device ID: \(deviceId)")

    do {
      // Fetch portfolio summary
      let summary = try await portfolioService.fetchPortfolioSummary(
        deviceId: deviceId,
        baseCurrency: baseCurrency
      )

      // Fetch grouped assets for top assets list
      let assets = try await portfolioService.fetchGroupedAssets(
        deviceId: deviceId,
        baseCurrency: baseCurrency
      )

      await MainActor.run {
        self.portfolioSummary = summary
        self.groupedAssets = assets
        self.isLoading = false
        print("✅ DashboardViewModel: Portfolio loaded successfully")
      }

    } catch let error as APIError {
      await MainActor.run {
        self.errorMessage = error.localizedDescription
        self.isLoading = false
        print("❌ DashboardViewModel: Failed to load portfolio - \(error.localizedDescription)")
      }
    } catch {
      await MainActor.run {
        self.errorMessage = "An unexpected error occurred. Please try again."
        self.isLoading = false
        print("❌ DashboardViewModel: Unexpected error - \(error)")
      }
    }
  }

  /// Refresh portfolio data (for pull-to-refresh)
  func refresh(deviceId: String, baseCurrency: String) async {
    guard !isRefreshing && !isLoading else { return }

    isRefreshing = true
    errorMessage = nil

    print("🔄 DashboardViewModel: Refreshing portfolio data...")
    print("💰 Using currency for refresh: \(baseCurrency)")

    do {
      // First refresh market prices with base currency
      let refreshResult = try await portfolioService.refreshMarketPrices(
        deviceId: deviceId,
        baseCurrency: baseCurrency
      )
      print("📊 Market prices refreshed: \(refreshResult.message)")

      // Then fetch updated portfolio data
      let summary = try await portfolioService.fetchPortfolioSummary(
        deviceId: deviceId,
        baseCurrency: baseCurrency
      )

      let assets = try await portfolioService.fetchGroupedAssets(
        deviceId: deviceId,
        baseCurrency: baseCurrency
      )

      await MainActor.run {
        self.portfolioSummary = summary
        self.groupedAssets = assets
        self.isRefreshing = false
        print("✅ DashboardViewModel: Portfolio refreshed successfully")
      }

    } catch let error as APIError {
      await MainActor.run {
        self.errorMessage = error.localizedDescription
        self.isRefreshing = false
        print("❌ DashboardViewModel: Failed to refresh portfolio - \(error.localizedDescription)")
      }
    } catch {
      await MainActor.run {
        self.errorMessage = "An unexpected error occurred. Please try again."
        self.isRefreshing = false
        print("❌ DashboardViewModel: Unexpected refresh error - \(error)")
      }
    }
  }

  /// Retry loading after error
  func retryLoad(deviceId: String, baseCurrency: String) {
    Task {
      await loadPortfolio(deviceId: deviceId, baseCurrency: baseCurrency)
    }
  }

  /// Clear error message
  func clearError() {
    errorMessage = nil
  }
}
