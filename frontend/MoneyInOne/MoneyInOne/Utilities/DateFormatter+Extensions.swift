//
//  DateFormatter+Extensions.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

extension DateFormatter {
    /// ISO 8601 formatter for API communication
    static let iso8601: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()
    
    /// Short date formatter (e.g., "10/1/25")
    static let shortDate: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .none
        return formatter
    }()
    
    /// Medium date formatter (e.g., "Oct 1, 2025")
    static let mediumDate: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter
    }()
    
    /// Full date formatter (e.g., "October 1, 2025")
    static let fullDate: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        formatter.timeStyle = .none
        return formatter
    }()
}

extension Date {
    /// Returns a relative time string (e.g., "2 minutes ago", "1 hour ago")
    func relativeTimeString() -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .full
        return formatter.localizedString(for: self, relativeTo: Date())
    }
    
    /// Returns a short relative time string (e.g., "2m ago", "1h ago")
    func shortRelativeTimeString() -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: self, relativeTo: Date())
    }
}

