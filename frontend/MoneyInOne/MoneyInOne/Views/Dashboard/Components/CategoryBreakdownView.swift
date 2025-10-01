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
    @State private var selectedView: BreakdownType = .assets
    
    // MARK: - Breakdown Type
    
    enum BreakdownType: String, CaseIterable {
        case assets = "Assets"
        case credits = "Credits"
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header with toggle
            HStack {
                Text("Portfolio Distribution")
                    .font(.headline)
                    .foregroundColor(.gray900)
                
                Spacer()
                
                Picker("View", selection: $selectedView) {
                    ForEach(BreakdownType.allCases, id: \.self) { type in
                        Text(type.rawValue).tag(type)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 180)
            }
            
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
            .cornerRadius(4)
        }
        .frame(height: 250)
        .chartLegend(.hidden)
    }
    
    // MARK: - Legend View
    
    private var legendView: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(currentData) { item in
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
            }
        }
        .padding(.top, 8)
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: selectedView == .assets ? "chart.pie" : "creditcard")
                .font(.system(size: 48))
                .foregroundColor(.gray400)
            
            Text("No \(selectedView.rawValue) Yet")
                .font(.headline)
                .foregroundColor(.gray600)
            
            Text("Add your first \(selectedView == .assets ? "asset" : "credit") to see distribution")
                .font(.caption)
                .foregroundColor(.gray500)
                .multilineTextAlignment(.center)
        }
        .frame(height: 250)
    }
    
    // MARK: - Computed Properties
    
    private var currentData: [ChartDataItem] {
        let breakdown: [String: (amount: Decimal, color: Color)]
        let total: Decimal
        
        if selectedView == .assets {
            breakdown = summary.assetSummary.mapValues { breakdown in
                let category = AssetCategory(rawValue: breakdown.category ?? "") ?? .other
                return (breakdown.totalAmount, category.color)
            }
            total = summary.totalAssets
        } else {
            breakdown = summary.creditSummary.mapValues { breakdown in
                let category = CreditCategory(rawValue: breakdown.category ?? "") ?? .other
                return (breakdown.totalAmount, category.color)
            }
            total = summary.totalCredits
        }
        
        guard total > 0 else { return [] }
        
        return breakdown.map { key, value in
            let percentage = (Double(truncating: value.amount as NSDecimalNumber) / Double(truncating: total as NSDecimalNumber)) * 100
            
            let displayName: String
            if selectedView == .assets {
                displayName = (AssetCategory(rawValue: key) ?? .other).displayName
            } else {
                displayName = (CreditCategory(rawValue: key) ?? .other).displayName
            }
            
            return ChartDataItem(
                id: key,
                name: displayName,
                amount: value.amount,
                percentage: percentage,
                color: value.color
            )
        }
        .sorted { $0.amount > $1.amount }
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

// MARK: - Extensions for Breakdown

extension AssetBreakdown {
    var category: String? {
        // This will be populated from the dictionary key
        return nil
    }
}

extension CreditBreakdown {
    var category: String? {
        // This will be populated from the dictionary key
        return nil
    }
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


