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
        HStack(spacing: 12) {
            // Category Icon with Gradient Background
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [asset.category.color, asset.category.color.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 40, height: 40)
                    .shadow(color: asset.category.color.opacity(0.3), radius: 8, x: 0, y: 4)
                
                Image(systemName: asset.category.iconName)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                // Header: Name + Currency Badge
                HStack(spacing: 8) {
                    Text(asset.name)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                    
                    // Currency Badge
                    Text(asset.currency)
                        .font(.caption2)
                        .fontWeight(.bold)
                        .padding(.horizontal, 7)
                        .padding(.vertical, 3)
                        .background(
                            Capsule()
                                .fill(currencyBadgeColor)
                        )
                        .foregroundColor(currencyTextColor)
                }
                
                // Amount (prominently displayed) - use displayAmount which prioritizes currentAmount
                Text(formatAmount(asset.displayAmount))
                    .font(.body)
                    .fontWeight(.bold)
                    .foregroundColor(.textPrimary)
                
                // Stock/Crypto specific info
                if asset.category == .stock || asset.category == .crypto {
                    if let symbol = asset.symbol, let shares = asset.shares {
                        HStack(spacing: 4) {
                            Image(systemName: "square.stack.3d.up.fill")
                                .font(.system(size: 9))
                            Text("\(symbol) • \(formatShares(shares))")
                                .font(.caption2)
                        }
                        .foregroundColor(.textSecondary)
                    }
                }
                
                // Dates: Purchase + Updated
                HStack(spacing: 8) {
                    HStack(spacing: 4) {
                        Image(systemName: "calendar")
                            .font(.system(size: 9))
                        Text(asset.purchaseDate.formatted(date: .abbreviated, time: .omitted))
                            .font(.caption2)
                    }
                    .foregroundColor(.textTertiary)
                    
                    Text("•")
                        .font(.caption2)
                        .foregroundColor(.textTertiary.opacity(0.5))
                    
                    HStack(spacing: 4) {
                        Image(systemName: "clock")
                            .font(.system(size: 9))
                        Text("Updated \(asset.updatedAt.shortRelativeTimeString())")
                            .font(.caption2)
                    }
                    .foregroundColor(.textTertiary)
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 10)
        .padding(.horizontal, 12)
        .background(Color.cardBackground)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(Color.borderColor.opacity(0.3), lineWidth: 1)
        )
        .shadow(color: Color.cardShadow, radius: 8, x: 0, y: 2)
        .shadow(color: Color.cardShadow.opacity(0.5), radius: 16, x: 0, y: 6)
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
        
        lastPriceUpdate: Date().addingTimeInterval(-5 * 60),
        isMarketTracked: true,
        convertedAmount: 21500.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-60 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-5 * 60)
    ))
    .padding()
}

