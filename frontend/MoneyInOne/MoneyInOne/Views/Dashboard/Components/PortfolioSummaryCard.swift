//
//  PortfolioSummaryCard.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//  Updated for UI Modernization on 2025/10/2
//

import SwiftUI

/// Portfolio summary card displaying total value, assets, credits, and net worth
struct PortfolioSummaryCard: View {
    // MARK: - Properties
    
    let summary: PortfolioSummary
    @Environment(\.colorScheme) private var colorScheme
    @State private var animatedValue: Double = 0
    
    // MARK: - Body
    
    var body: some View {
        GlassCard(style: .prominent, shadowStyle: .prominent) {
            VStack(alignment: .leading, spacing: 20) {
                // Header with net worth and last updated
                headerSection
                
                // Assets and Credits breakdown
                metricsSection
            }
        }
        .onAppear {
            animateValue()
        }
        .onChange(of: summary.netWorth) { _, _ in
            animateValue()
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 12) {
                Text("Net Portfolio Value")
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(.textPrimary)
                
                Text(CurrencyFormatter.format(
                    amount: summary.netWorth,
                    currency: summary.baseCurrency
                ))
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .foregroundColor(.textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 6) {
                Label("Updated", systemImage: "clock.fill")
                    .font(.caption2)
                    .foregroundColor(.textTertiary)
                    .labelStyle(.titleOnly)
                
                Text(summary.lastUpdated.shortRelativeTimeString())
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.textSecondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.cardBackgroundSecondary)
                    .cornerRadius(6)
            }
        }
    }
    
    // MARK: - Metrics Section
    
    private var metricsSection: some View {
        HStack(spacing: 12) {
            // Assets
            ModernMetricCard(
                icon: "wallet.pass.fill",
                iconGradient: Color.successGradient,
                title: "Assets",
                amount: summary.totalAssets,
                currency: summary.baseCurrency,
                count: summary.totalAssetCount,
                shadowColor: .successColor
            )
            
            // Credits
            ModernMetricCard(
                icon: "creditcard.fill",
                iconGradient: Color.dangerGradient,
                title: "Credits",
                amount: summary.totalCredits,
                currency: summary.baseCurrency,
                count: summary.totalCreditCount,
                shadowColor: .dangerColor
            )
        }
    }
    
    // MARK: - Animation
    
    private func animateValue() {
        withAnimation(.spring(response: 0.8, dampingFraction: 0.8)) {
            animatedValue = Double(truncating: summary.netWorth as NSDecimalNumber)
        }
    }
}

// MARK: - Modern Metric Card

struct ModernMetricCard: View {
    let icon: String
    let iconGradient: LinearGradient
    let title: String
    let amount: Decimal
    let currency: String
    let count: Int
    let shadowColor: Color
    
    @Environment(\.colorScheme) private var colorScheme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            // Icon with gradient background
            HStack(spacing: 10) {
                ZStack {
                    Circle()
                        .fill(iconGradient)
                        .frame(width: 32, height: 32)
                        .shadow(color: shadowColor.opacity(0.3), radius: 8, x: 0, y: 4)
                    
                    Image(systemName: icon)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                }
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textSecondary)
            }
            
            // Amount and count
            VStack(alignment: .leading, spacing: 6) {
                Text(CurrencyFormatter.format(amount: amount, currency: currency))
                    .font(.system(size: 18, weight: .bold, design: .rounded))
                    .foregroundColor(.textPrimary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                HStack(spacing: 4) {
                    Image(systemName: "square.stack.3d.up.fill")
                        .font(.system(size: 10))
                        .foregroundColor(.textTertiary)
                    
                    Text("\(count) \(count == 1 ? "item" : "items")")
                        .font(.caption2)
                        .fontWeight(.medium)
                        .foregroundColor(.textTertiary)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.cardBackgroundSecondary)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .strokeBorder(Color.borderColor.opacity(0.5), lineWidth: 1)
        )
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


