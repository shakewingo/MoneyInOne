//
//  ErrorView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Reusable error view with retry action
struct ErrorView: View {
    let error: Error
    let retryAction: (() -> Void)?
    
    init(error: Error, retryAction: (() -> Void)? = nil) {
        self.error = error
        self.retryAction = retryAction
    }
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 50))
                .foregroundColor(.warningColor)
            
            Text("Oops! Something went wrong")
                .font(.headline)
                .multilineTextAlignment(.center)
            
            Text(error.localizedDescription)
                .font(.subheadline)
                .foregroundColor(.gray500)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            if let retryAction = retryAction {
                Button(action: retryAction) {
                    HStack {
                        Image(systemName: "arrow.clockwise")
                        Text("Try Again")
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
        .padding()
    }
}

/// Inline error message view
struct InlineErrorView: View {
    let message: String
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "exclamationmark.circle.fill")
                .foregroundColor(.dangerColor)
            Text(message)
                .font(.caption)
                .foregroundColor(.dangerColor)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.dangerColor.opacity(0.1))
        .cornerRadius(8)
    }
}

#Preview("Error View") {
    ErrorView(
        error: APIError.serverError(500, "Failed to connect to server"),
        retryAction: {}
    )
}

#Preview("Error View Without Retry") {
    ErrorView(
        error: APIError.invalidResponse
    )
}

#Preview("Inline Error") {
    InlineErrorView(message: "Failed to load data")
}

