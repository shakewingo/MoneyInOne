//
//  CategoryBreakdownView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI
import Charts

/// View displaying portfolio distribution by category as a chart
struct CategoryBreakdownView: View {
    // MARK: - Properties
    
    let summary: PortfolioSummary
    @State private var selectedSegment: String?
    
    // MARK: - Body
    
    var body: some View {
        GlassCard(style: .standard, shadowStyle: .soft) {
            VStack(alignment: .leading, spacing: 18) {
                // Header with icon
                HStack {
                    ZStack {
                        Circle()
                            .fill(Color.primaryGradient)
                            .frame(width: 32, height: 32)
                            .shadow(color: Color.primaryColor.opacity(0.3), radius: 6, x: 0, y: 3)
                        
                        Image(systemName: "chart.pie.fill")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.white)
                    }
                    
                    Text("Portfolio Distribution")
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                }
                
                // Chart or empty state
                if currentData.isEmpty {
                    emptyStateView
                } else {
                    chartView
                    legendView
                }
            }
        }
    }
    
    // MARK: - Chart View
    
    private var chartView: some View {
        Chart(currentData) { item in
            SectorMark(
                angle: .value("Amount", item.amount),
                innerRadius: .ratio(0.55),
                angularInset: 2
            )
            .foregroundStyle(item.color)
            .opacity(selectedSegment == nil || selectedSegment == item.id ? 1.0 : 0.35)
            .cornerRadius(5)
        }
        .frame(height: 280)
        .chartLegend(.hidden)
        .chartAngleSelection(value: $selectedSegment)
        .animation(.spring(response: 0.4, dampingFraction: 0.7), value: selectedSegment)
    }
    
    // MARK: - Legend View
    
    private var legendView: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(currentData) { item in
                Button(action: {
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                        if selectedSegment == item.id {
                            selectedSegment = nil
                        } else {
                            selectedSegment = item.id
                        }
                    }
                }) {
                    HStack(spacing: 14) {
                        // Color indicator with glow
                        ZStack {
                            Circle()
                                .fill(item.color)
                                .frame(width: 14, height: 14)
                            
                            if selectedSegment == item.id {
                                Circle()
                                    .stroke(item.color, lineWidth: 2)
                                    .frame(width: 20, height: 20)
                            }
                        }
                        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: selectedSegment)
                        
                        Text(item.name)
                            .font(.subheadline)
                            .fontWeight(selectedSegment == item.id ? .semibold : .regular)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 3) {
                            Text(CurrencyFormatter.format(
                                amount: item.amount,
                                currency: summary.baseCurrency
                            ))
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                            
                            Text("\(item.percentage, specifier: "%.1f")%")
                                .font(.caption2)
                                .fontWeight(.medium)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(selectedSegment == item.id ? item.color.opacity(0.15) : Color.cardBackgroundSecondary)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .strokeBorder(
                                selectedSegment == item.id ? item.color.opacity(0.4) : Color.clear,
                                lineWidth: 2
                            )
                    )
                    .scaleEffect(selectedSegment == item.id ? 1.02 : 1.0)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.top, 12)
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.gray200)
                    .frame(width: 80, height: 80)
                
                Image(systemName: "chart.pie")
                    .font(.system(size: 36))
                    .foregroundColor(.textTertiary)
            }
            
            VStack(spacing: 6) {
                Text("No Portfolio Data Yet")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                
                Text("Add assets or credits to see your portfolio distribution")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
        }
        .frame(height: 280)
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Computed Properties
    
    private var currentData: [ChartDataItem] {
        var items: [ChartDataItem] = []
        
        // Calculate total portfolio value (assets + credits)
        let total = summary.totalAssets + summary.totalCredits
        
        guard total > 0 else { return [] }
        
        // Add asset categories
        for (categoryKey, categoryBreakdown) in summary.assetSummary {
            let category = AssetCategory(rawValue: categoryKey) ?? .other
            let percentage = (Double(truncating: categoryBreakdown.totalAmount as NSDecimalNumber) / Double(truncating: total as NSDecimalNumber)) * 100
            
            items.append(ChartDataItem(
                id: "asset_\(categoryKey)",
                name: category.displayName,
                amount: categoryBreakdown.totalAmount,
                percentage: percentage,
                color: category.color
            ))
        }
        
        // Add credit categories
        for (categoryKey, categoryBreakdown) in summary.creditSummary {
            let category = CreditCategory(rawValue: categoryKey) ?? .other
            let percentage = (Double(truncating: categoryBreakdown.totalAmount as NSDecimalNumber) / Double(truncating: total as NSDecimalNumber)) * 100
            
            items.append(ChartDataItem(
                id: "credit_\(categoryKey)",
                name: category.displayName,
                amount: categoryBreakdown.totalAmount,
                percentage: percentage,
                color: category.color
            ))
        }
        
        // Sort by amount (largest first)
        return items.sorted { $0.amount > $1.amount }
    }
}

// MARK: - Chart Data Item

struct ChartDataItem: Identifiable {
    let id: String
    let name: String
    let amount: Decimal
    let percentage: Double
    let color: Color
}

// MARK: - Preview

#Preview("With Assets") {
    CategoryBreakdownView(
        summary: PortfolioSummary(
            baseCurrency: "CNY",
            assetSummary: [
                "cash": AssetBreakdown(totalAmount: 50000, count: 2),
                "stock": AssetBreakdown(totalAmount: 150000, count: 5),
                "crypto": AssetBreakdown(totalAmount: 30000, count: 3)
            ],
            creditSummary: [
                "credit_card": CreditBreakdown(totalAmount: 15000, count: 2)
            ],
            netWorth: 215000,
            lastUpdated: Date()
        )
    )
    .padding()
}

#Preview("Empty") {
    CategoryBreakdownView(
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


