//
//  PortfolioSummaryCard.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Portfolio summary card displaying total value, assets, credits, and net worth
struct PortfolioSummaryCard: View {
    // MARK: - Properties
    
    let summary: PortfolioSummary
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header with net worth and last updated
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Total Portfolio Value")
                        .font(.headline)
                        .foregroundColor(.gray600)
                    
                    Text(CurrencyFormatter.format(
                        amount: summary.netWorth,
                        currency: summary.baseCurrency
                    ))
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundColor(.gray900)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Last updated")
                        .font(.caption)
                        .foregroundColor(.gray500)
                    
                    Text(summary.lastUpdated.shortRelativeTimeString())
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.gray700)
                }
            }
            
            // Assets, Credits, Net Worth breakdown
            HStack(spacing: 12) {
                // Assets
                SummaryMetricCard(
                    icon: "chart.line.uptrend.xyaxis",
                    iconColor: .green,
                    title: "Assets",
                    amount: summary.totalAssets,
                    currency: summary.baseCurrency,
                    count: summary.totalAssetCount
                )
                
                // Credits
                SummaryMetricCard(
                    icon: "creditcard.fill",
                    iconColor: .red,
                    title: "Credits",
                    amount: summary.totalCredits,
                    currency: summary.baseCurrency,
                    count: summary.totalCreditCount
                )
            }
        }
        .padding(20)
        .background(Color.white)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 2)
    }
}

// MARK: - Summary Metric Card

struct SummaryMetricCard: View {
    let icon: String
    let iconColor: Color
    let title: String
    let amount: Decimal
    let currency: String
    let count: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 16))
                    .foregroundColor(iconColor)
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.gray600)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(CurrencyFormatter.format(amount: amount, currency: currency))
                    .font(.system(size: 20, weight: .bold, design: .rounded))
                    .foregroundColor(.gray900)
                
                Text("\(count) \(count == 1 ? "item" : "items")")
                    .font(.caption)
                    .foregroundColor(.gray500)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.gray100)
        .cornerRadius(12)
    }
}

// MARK: - Preview

#Preview("With Data") {
    PortfolioSummaryCard(
        summary: PortfolioSummary(
            baseCurrency: "CNY",
            assetSummary: [
                "cash": AssetBreakdown(totalAmount: 50000, count: 2),
                "stock": AssetBreakdown(totalAmount: 150000, count: 5),
                "crypto": AssetBreakdown(totalAmount: 30000, count: 3)
            ],
            creditSummary: [
                "credit_card": CreditBreakdown(totalAmount: 15000, count: 2),
                "mortgage": CreditBreakdown(totalAmount: 200000, count: 1)
            ],
            netWorth: 15000,
            lastUpdated: Date().addingTimeInterval(-120) // 2 minutes ago
        )
    )
    .padding()
}

#Preview("Empty Portfolio") {
    PortfolioSummaryCard(
        summary: PortfolioSummary(
            baseCurrency: "USD",
            assetSummary: [:],
            creditSummary: [:],
            netWorth: 0,
            lastUpdated: Date()
        )
    )
    .padding()
}


