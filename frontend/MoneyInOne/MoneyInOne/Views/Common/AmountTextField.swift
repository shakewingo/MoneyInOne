//
//  AmountTextField.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Custom text field for currency amount input
struct AmountTextField: View {
    @Binding var amount: String
    let currencySymbol: String
    let placeholder: String
    let isRequired: Bool
    
    init(
        amount: Binding<String>,
        currencySymbol: String,
        placeholder: String = "0.00",
        isRequired: Bool = true
    ) {
        self._amount = amount
        self.currencySymbol = currencySymbol
        self.placeholder = placeholder
        self.isRequired = isRequired
    }
    
    var body: some View {
        HStack(spacing: 8) {
            Text(currencySymbol)
                .font(.body)
                .foregroundColor(.secondary)
                .frame(width: 24, alignment: .leading)
            
            TextField(placeholder, text: $amount)
                .keyboardType(.decimalPad)
                .font(.body)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        AmountTextField(
            amount: .constant("1234.56"),
            currencySymbol: "$"
        )
        
        AmountTextField(
            amount: .constant(""),
            currencySymbol: "¥",
            placeholder: "Enter amount"
        )
        
        AmountTextField(
            amount: .constant("999.99"),
            currencySymbol: "€"
        )
    }
    .padding()
}

