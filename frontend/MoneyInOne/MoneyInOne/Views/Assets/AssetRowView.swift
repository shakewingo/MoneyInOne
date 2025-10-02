//
//  AssetRowView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Row view component for displaying individual asset cards in the list
struct AssetListRowView: View {
    // MARK: - Properties
    
    let asset: Asset
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header: Name + Currency Badge + Stock Info
            HStack(spacing: 8) {
                Text(asset.name)
                    .font(.headline)
                    .foregroundColor(.primary)
                
                // Currency Badge
                Text(asset.currency)
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(currencyBadgeColor)
                    .foregroundColor(currencyTextColor)
                    .cornerRadius(8)
                
                // Stock/Crypto specific info (symbol and shares)
                if asset.category == .stock || asset.category == .crypto {
                    if let symbol = asset.symbol, let shares = asset.shares {
                        Text("• \(symbol) • \(formatShares(shares))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
            }
            
            // Amount (prominently displayed)
            Text(formatAmount(asset.convertedAmount ?? asset.amount))
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
            
            // Purchase Date
            HStack(spacing: 4) {
                Image(systemName: "calendar")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Text("Purchased: \(asset.purchaseDate.formatted(date: .abbreviated, time: .omitted))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            // Last Updated
            if let lastUpdate = asset.lastPriceUpdate {
                HStack(spacing: 4) {
                    Image(systemName: "clock")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("Updated: \(lastUpdate.relativeTimeString())")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } else {
                HStack(spacing: 4) {
                    Image(systemName: "clock")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("Updated: \(asset.updatedAt.relativeTimeString())")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 12)
        .padding(.horizontal, 16)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
    }
    
    // MARK: - Helper Methods
    
    /// Formats the asset amount with currency symbol
    private func formatAmount(_ amount: Decimal) -> String {
        return CurrencyFormatter.format(amount: amount, currency: asset.currency)
    }
    
    /// Formats share count (removes unnecessary decimals for whole numbers)
    private func formatShares(_ shares: Double) -> String {
        if shares.truncatingRemainder(dividingBy: 1) == 0 {
            return "\(Int(shares)) shares"
        } else {
            return String(format: "%.2f shares", shares)
        }
    }
    
    /// Currency badge background color based on currency
    private var currencyBadgeColor: Color {
        switch asset.currency.uppercased() {
        case "USD": return Color.green.opacity(0.15)
        case "EUR": return Color.blue.opacity(0.15)
        case "GBP": return Color.purple.opacity(0.15)
        case "JPY": return Color.red.opacity(0.15)
        case "CNY": return Color.orange.opacity(0.15)
        case "CAD": return Color.pink.opacity(0.15)
        case "AUD": return Color.teal.opacity(0.15)
        default: return Color.gray.opacity(0.15)
        }
    }
    
    /// Currency badge text color
    private var currencyTextColor: Color {
        switch asset.currency.uppercased() {
        case "USD": return Color.green
        case "EUR": return Color.blue
        case "GBP": return Color.purple
        case "JPY": return Color.red
        case "CNY": return Color.orange
        case "CAD": return Color.pink
        case "AUD": return Color.teal
        default: return Color.gray
        }
    }
}

// MARK: - Preview

#Preview("Cash Asset") {
    AssetListRowView(asset: Asset(
        id: UUID(),
        userId: UUID(),
        name: "USD Savings Account",
        category: .cash,
        amount: 25480.00,
        currency: "USD",
        purchaseDate: Date().addingTimeInterval(-90 * 24 * 3600),
        notes: "Primary savings",
        symbol: nil,
        shares: nil,
        originalAmount: nil,
        currentAmount: nil,
        lastPriceUpdate: nil,
        isMarketTracked: false,
        convertedAmount: 25480.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-90 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-1 * 3600)
    ))
    .padding()
}

#Preview("Stock Asset") {
    AssetListRowView(asset: Asset(
        id: UUID(),
        userId: UUID(),
        name: "Apple Inc.",
        category: .stock,
        amount: 28950.00,
        currency: "USD",
        purchaseDate: Date().addingTimeInterval(-120 * 24 * 3600),
        notes: "Tech investment",
        symbol: "AAPL",
        shares: 150,
        originalAmount: 25000.00,
        currentAmount: 28950.00,
        lastPriceUpdate: Date().addingTimeInterval(-15 * 60),
        isMarketTracked: true,
        convertedAmount: 28950.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-120 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-15 * 60)
    ))
    .padding()
}

#Preview("Crypto Asset") {
    AssetListRowView(asset: Asset(
        id: UUID(),
        userId: UUID(),
        name: "Bitcoin",
        category: .crypto,
        amount: 21500.00,
        currency: "USD",
        purchaseDate: Date().addingTimeInterval(-60 * 24 * 3600),
        notes: "Crypto investment",
        symbol: "BTC",
        shares: 0.5,
        originalAmount: 20000.00,
        currentAmount: 21500.00,
        lastPriceUpdate: Date().addingTimeInterval(-5 * 60),
        isMarketTracked: true,
        convertedAmount: 21500.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-60 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-5 * 60)
    ))
    .padding()
}

