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
        VStack(alignment: .leading, spacing: 16) {
            // Header (smaller font)
            Text("Portfolio Distribution")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.gray900)
            
            // Chart or empty state
            if currentData.isEmpty {
                emptyStateView
            } else {
                chartView
                legendView
            }
        }
        .padding(20)
        .background(Color.white)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 2)
    }
    
    // MARK: - Chart View
    
    private var chartView: some View {
        Chart(currentData) { item in
            SectorMark(
                angle: .value("Amount", item.amount),
                innerRadius: .ratio(0.5),
                angularInset: 1.5
            )
            .foregroundStyle(item.color)
            .opacity(selectedSegment == nil || selectedSegment == item.id ? 1.0 : 0.3)
            .cornerRadius(4)
        }
        .frame(height: 250)
        .chartLegend(.hidden)
        .chartAngleSelection(value: $selectedSegment)
    }
    
    // MARK: - Legend View
    
    private var legendView: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(currentData) { item in
                Button(action: {
                    withAnimation {
                        if selectedSegment == item.id {
                            selectedSegment = nil
                        } else {
                            selectedSegment = item.id
                        }
                    }
                }) {
                    HStack(spacing: 12) {
                        Circle()
                            .fill(item.color)
                            .frame(width: 12, height: 12)
                        
                        Text(item.name)
                            .font(.subheadline)
                            .foregroundColor(.gray700)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 2) {
                            Text(CurrencyFormatter.format(
                                amount: item.amount,
                                currency: summary.baseCurrency
                            ))
                            .font(.subheadline)
                            .fontWeight(.semibold)
                            .foregroundColor(.gray900)
                            
                            Text("\(item.percentage, specifier: "%.1f")%")
                                .font(.caption)
                                .foregroundColor(.gray500)
                        }
                    }
                    .padding(8)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(selectedSegment == item.id ? item.color.opacity(0.1) : Color.clear)
                    )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.top, 8)
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "chart.pie")
                .font(.system(size: 48))
                .foregroundColor(.gray400)
            
            Text("No Portfolio Data Yet")
                .font(.headline)
                .foregroundColor(.gray600)
            
            Text("Add assets or credits to see your portfolio distribution")
                .font(.caption)
                .foregroundColor(.gray500)
                .multilineTextAlignment(.center)
        }
        .frame(height: 250)
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


