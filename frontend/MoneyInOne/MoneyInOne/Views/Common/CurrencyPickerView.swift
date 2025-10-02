//
//  CurrencyPickerView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Picker for selecting currency in forms
struct CurrencyPickerView: View {
    @Binding var selectedCurrency: Currency
    
    var body: some View {
        Picker("Currency", selection: $selectedCurrency) {
            ForEach(Currency.allCases) { currency in
                Text(currency.rawValue)
                    .tag(currency)
            }
        }
        .pickerStyle(.menu)
    }
}

// MARK: - Preview

#Preview {
    Form {
        Section {
            CurrencyPickerView(selectedCurrency: .constant(.CNY))
        }
    }
}

