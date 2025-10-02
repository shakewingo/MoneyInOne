//
//  CreditRowView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Row view component for displaying individual credit cards in the list
struct CreditListRowView: View {
    // MARK: - Properties
    
    let credit: Credit
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header: Name + Currency Badge
            HStack(spacing: 8) {
                Text(credit.name)
                    .font(.headline)
                    .foregroundColor(.primary)
                
                // Currency Badge
                Text(credit.currency)
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(currencyBadgeColor)
                    .foregroundColor(currencyTextColor)
                    .cornerRadius(8)
                
                Spacer()
            }
            
            // Amount (prominently displayed)
            Text(formatAmount(credit.convertedAmount ?? credit.amount))
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.red)
            
            // Issue Date
            HStack(spacing: 4) {
                Image(systemName: "calendar")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Text("Issued: \(credit.issueDate.formatted(date: .abbreviated, time: .omitted))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            // Last Updated
            HStack(spacing: 4) {
                Image(systemName: "clock")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                Text("Updated: \(credit.updatedAt.relativeTimeString())")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 12)
        .padding(.horizontal, 16)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
    }
    
    // MARK: - Helper Methods
    
    /// Formats the credit amount with currency symbol
    private func formatAmount(_ amount: Decimal) -> String {
        return CurrencyFormatter.format(amount: amount, currency: credit.currency)
    }
    
    /// Currency badge background color based on currency
    private var currencyBadgeColor: Color {
        switch credit.currency.uppercased() {
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
        switch credit.currency.uppercased() {
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

#Preview("Credit Card") {
    CreditListRowView(credit: Credit(
        id: UUID(),
        userId: UUID(),
        name: "Chase Sapphire Reserve",
        category: .creditCard,
        amount: 5230.50,
        currency: "USD",
        issueDate: Date().addingTimeInterval(-365 * 24 * 3600),
        notes: "Primary credit card",
        convertedAmount: 5230.50,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-365 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-2 * 3600)
    ))
    .padding()
}

#Preview("Mortgage") {
    CreditListRowView(credit: Credit(
        id: UUID(),
        userId: UUID(),
        name: "Home Mortgage",
        category: .mortgage,
        amount: 485000.00,
        currency: "USD",
        issueDate: Date().addingTimeInterval(-730 * 24 * 3600),
        notes: "30-year fixed rate",
        convertedAmount: 485000.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-730 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-24 * 3600)
    ))
    .padding()
}

#Preview("Loan") {
    CreditListRowView(credit: Credit(
        id: UUID(),
        userId: UUID(),
        name: "Car Loan",
        category: .loan,
        amount: 18500.00,
        currency: "USD",
        issueDate: Date().addingTimeInterval(-180 * 24 * 3600),
        notes: "5-year auto loan",
        convertedAmount: 18500.00,
        conversionRate: 1.0,
        createdAt: Date().addingTimeInterval(-180 * 24 * 3600),
        updatedAt: Date().addingTimeInterval(-12 * 3600)
    ))
    .padding()
}

