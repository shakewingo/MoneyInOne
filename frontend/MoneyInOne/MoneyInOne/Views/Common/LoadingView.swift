//
//  LoadingView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import SwiftUI

/// Reusable loading view with optional message
struct LoadingView: View {
    var message: String = "Loading..."
    
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
                .progressViewStyle(CircularProgressViewStyle(tint: .primaryColor))
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.gray500)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(UIColor.systemBackground))
    }
}

/// Small inline loading indicator
struct InlineLoadingView: View {
    var body: some View {
        HStack(spacing: 8) {
            ProgressView()
                .scaleEffect(0.8)
            Text("Loading...")
                .font(.caption)
                .foregroundColor(.gray500)
        }
        .padding(8)
    }
}

#Preview("Loading View") {
    LoadingView()
}

#Preview("Loading View with Custom Message") {
    LoadingView(message: "Fetching your portfolio...")
}

#Preview("Inline Loading") {
    InlineLoadingView()
}

