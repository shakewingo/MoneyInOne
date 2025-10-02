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
        HStack(spacing: 14) {
            // Category Icon with Gradient Background
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [credit.category.color, credit.category.color.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 48, height: 48)
                    .shadow(color: credit.category.color.opacity(0.3), radius: 8, x: 0, y: 4)
                
                Image(systemName: credit.category.iconName)
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 6) {
                // Header: Name + Currency Badge
                HStack(spacing: 8) {
                    Text(credit.name)
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                    
                    // Currency Badge
                    Text(credit.currency)
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
                
                // Amount (prominently displayed in red for debt)
                Text(formatAmount(credit.convertedAmount ?? credit.amount))
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.dangerColor)
                
                // Issue Date
                Label(credit.issueDate.formatted(date: .abbreviated, time: .omitted), systemImage: "calendar")
                    .font(.caption)
                    .foregroundColor(.textTertiary)
                    .labelStyle(.titleOnly)
            }
            
            Spacer()
        }
        .padding(.vertical, 14)
        .padding(.horizontal, 16)
        .background(Color.cardBackground)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(Color.borderColor.opacity(0.3), lineWidth: 1)
        )
        .shadow(color: Color.cardShadow, radius: 8, x: 0, y: 2)
        .shadow(color: Color.cardShadow.opacity(0.5), radius: 16, x: 0, y: 6)
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

