//
//  TopAssetsListView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// View displaying top assets by value
struct TopAssetsListView: View {
    // MARK: - Properties
    
    let assets: [Asset]
    let baseCurrency: String
    let onViewAll: () -> Void
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header
            HStack {
                Text("Top Assets")
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Button(action: onViewAll) {
                    Text("View All")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primaryColor)
                }
            }
            
            // Assets list or empty state
            if assets.isEmpty {
                emptyStateView
            } else {
                assetsList
            }
        }
        .padding(20)
        .background(Color.cardBackground)
        .cornerRadius(16)
        .shadow(color: Color.cardShadow, radius: 10, x: 0, y: 2)
    }
    
    // MARK: - Assets List
    
    private var assetsList: some View {
        VStack(spacing: 12) {
            ForEach(assets.prefix(5)) { asset in
                AssetRowView(asset: asset, baseCurrency: baseCurrency)
            }
        }
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "wallet.pass")
                .font(.system(size: 48))
                .foregroundColor(.gray400)
            
            Text("No Assets Yet")
                .font(.headline)
                .foregroundColor(.gray600)
            
            Text("Start tracking your wealth by adding your first asset")
                .font(.caption)
                .foregroundColor(.gray500)
                .multilineTextAlignment(.center)
        }
        .frame(height: 200)
    }
}

// MARK: - Asset Row View

struct AssetRowView: View {
    let asset: Asset
    let baseCurrency: String
    
    private var displayAmount: Decimal {
        asset.convertedAmount ?? asset.displayAmount
    }
    
    private var displayCurrency: String {
        asset.convertedAmount != nil ? baseCurrency : asset.currency
    }
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            ZStack {
                Circle()
                    .fill(asset.category.color.opacity(0.2))
                    .frame(width: 40, height: 40)
                
                Image(systemName: asset.category.iconName)
                    .font(.system(size: 18))
                    .foregroundColor(asset.category.color)
            }
            
            // Asset info
            VStack(alignment: .leading, spacing: 4) {
                Text(asset.name)
                    .font(.body)
                    .fontWeight(.medium)
                    .foregroundColor(.gray900)
                    .lineLimit(1)
                
                // For stocks and crypto, show details in a more adaptive layout
                // For other categories, just show category name
                if asset.category == .stock || asset.category == .crypto {
                    VStack(alignment: .leading, spacing: 2) {
                        // First line: Category • Symbol
                        HStack(spacing: 4) {
                            Text(asset.category.displayName)
                                .font(.caption)
                                .foregroundColor(.gray500)
                            
                            if let symbol = asset.symbol {
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.gray400)
                                Text(symbol)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .foregroundColor(.gray600)
                            }
                        }
                        
                        // Second line: Shares count (if available)
                        if let shares = asset.shares {
                            Text("\(shares, specifier: "%.2f") shares")
                                .font(.caption2)
                                .foregroundColor(.gray400)
                        }
                    }
                } else {
                    Text(asset.category.displayName)
                        .font(.caption)
                        .foregroundColor(.gray500)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            Spacer()
            
            // Amount
            VStack(alignment: .trailing, spacing: 4) {
                Text(CurrencyFormatter.format(
                    amount: displayAmount,
                    currency: displayCurrency
                ))
                .font(.footnote)
                .fontWeight(.semibold)
                .foregroundColor(.gray900)
                
                // Removed percentage change display due to incorrect calculation
            }
        }
        .padding(12)
        .background(Color.gray50)
        .cornerRadius(12)
    }
}

// MARK: - Preview

#Preview("With Assets") {
    TopAssetsListView(
        assets: [
            Asset(
                id: UUID(),
                userId: UUID(),
                name: "Bitcoin",
                category: .crypto,
                amount: 32450,
                currency: "USD",
                purchaseDate: Date(),
                notes: nil,
                symbol: "BTC",
                shares: 0.5,
                originalAmount: 30000,
                currentAmount: 32450,
                lastPriceUpdate: Date(),
                isMarketTracked: true,
                convertedAmount: 32450,
                conversionRate: 1.0,
                createdAt: Date(),
                updatedAt: Date()
            ),
            Asset(
                id: UUID(),
                userId: UUID(),
                name: "Apple Stock",
                category: .stock,
                amount: 28750,
                currency: "USD",
                purchaseDate: Date(),
                notes: nil,
                symbol: "AAPL",
                shares: 150,
                originalAmount: 27000,
                currentAmount: 28750,
                lastPriceUpdate: Date(),
                isMarketTracked: true,
                convertedAmount: 28750,
                conversionRate: 1.0,
                createdAt: Date(),
                updatedAt: Date()
            ),
            Asset(
                id: UUID(),
                userId: UUID(),
                name: "Savings Account",
                category: .cash,
                amount: 50000,
                currency: "CNY",
                purchaseDate: Date(),
                notes: nil,
                symbol: nil,
                shares: nil,
                originalAmount: nil,
                currentAmount: nil,
                lastPriceUpdate: nil,
                isMarketTracked: false,
                convertedAmount: 50000,
                conversionRate: 1.0,
                createdAt: Date(),
                updatedAt: Date()
            )
        ],
        baseCurrency: "CNY",
        onViewAll: {}
    )
    .padding()
}

#Preview("Empty") {
    TopAssetsListView(
        assets: [],
        baseCurrency: "USD",
        onViewAll: {}
    )
    .padding()
}


