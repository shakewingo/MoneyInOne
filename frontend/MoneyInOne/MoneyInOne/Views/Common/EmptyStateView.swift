//
//  EmptyStateView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Reusable empty state view
struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    let actionTitle: String?
    let action: (() -> Void)?
    
    init(
        icon: String,
        title: String,
        message: String,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil
    ) {
        self.icon = icon
        self.title = title
        self.message = message
        self.actionTitle = actionTitle
        self.action = action
    }
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: icon)
                .font(.system(size: 60))
                .foregroundColor(.gray300)
            
            Text(title)
                .font(.title2)
                .fontWeight(.semibold)
                .multilineTextAlignment(.center)
            
            Text(message)
                .font(.body)
                .foregroundColor(.gray500)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
            
            if let actionTitle = actionTitle, let action = action {
                Button(action: action) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text(actionTitle)
                    }
                    .font(.body)
                    .foregroundColor(.white)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(Color.primaryColor)
                    .cornerRadius(10)
                }
                .padding(.top, 8)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(UIColor.systemBackground))
    }
}

#Preview("Empty Assets") {
    EmptyStateView(
        icon: "wallet.pass",
        title: "No Assets Yet",
        message: "Start building your portfolio by adding your first asset",
        actionTitle: "Add Asset",
        action: {}
    )
}

#Preview("Empty Credits") {
    EmptyStateView(
        icon: "creditcard",
        title: "No Credits",
        message: "You don't have any credits recorded yet",
        actionTitle: "Add Credit",
        action: {}
    )
}

#Preview("Empty State Without Action") {
    EmptyStateView(
        icon: "chart.bar",
        title: "No Data",
        message: "There's nothing to display right now"
    )
}

