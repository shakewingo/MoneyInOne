//
//  CurrencyPickerMenu.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Currency picker menu for navigation bar
struct CurrencyPickerMenu: View {
    @Environment(AppCoordinator.self) private var coordinator
    let onCurrencyChange: (() -> Void)?
    
    init(onCurrencyChange: (() -> Void)? = nil) {
        self.onCurrencyChange = onCurrencyChange
    }
    
    var body: some View {
        Menu {
            Picker("Currency", selection: Binding(
                get: { coordinator.baseCurrency },
                set: { newCurrency in
                    coordinator.updateBaseCurrency(newCurrency)
                    onCurrencyChange?()
                }
            )) {
                ForEach(Currency.allCases) { currency in
                    Label(
                        title: { Text("\(currency.rawValue) - \(currency.name)") },
                        icon: { Text(currency.symbol) }
                    )
                    .tag(currency)
                }
            }
        } label: {
            HStack(spacing: 4) {
                Text(coordinator.baseCurrency.symbol)
                    .font(.system(size: 16, weight: .medium))
                Text(coordinator.baseCurrency.rawValue)
                    .font(.system(size: 14))
                Image(systemName: "chevron.down")
                    .font(.system(size: 10))
            }
            .foregroundColor(.primaryColor)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color.primaryColor.opacity(0.1))
            .cornerRadius(8)
        }
    }
}

#Preview {
    CurrencyPickerMenu()
        .environment(AppCoordinator())
}
