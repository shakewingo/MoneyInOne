//
//  Color+Theme.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//  Updated for UI Modernization on 2025/10/2
//

import SwiftUI

extension Color {
    // MARK: - Adaptive Theme Colors (Light/Dark Mode)
    
    /// Primary brand color (Blue) - Adapts to dark mode
    static let primaryColor = Color.adaptiveColor(
        light: Color(hex: "3B82F6"),
        dark: Color(hex: "60A5FA")
    )
    
    /// Secondary brand color (Indigo) - Adapts to dark mode
    static let secondaryColor = Color.adaptiveColor(
        light: Color(hex: "1E40AF"),
        dark: Color(hex: "4F46E5")
    )
    
    /// Success color (Green) - Adapts to dark mode
    static let successColor = Color.adaptiveColor(
        light: Color(hex: "10B981"),
        dark: Color(hex: "34D399")
    )
    
    /// Danger/Error color (Red) - Adapts to dark mode
    static let dangerColor = Color.adaptiveColor(
        light: Color(hex: "EF4444"),
        dark: Color(hex: "F87171")
    )
    
    /// Warning color (Orange) - Adapts to dark mode
    static let warningColor = Color.adaptiveColor(
        light: Color(hex: "F59E0B"),
        dark: Color(hex: "FBBF24")
    )
    
    // MARK: - Semantic Colors
    
    /// Primary background color (adapts to light/dark mode)
    static let appBackground = Color.adaptiveColor(
        light: Color(hex: "F9FAFB"),
        dark: Color(hex: "000000")
    )
    
    /// Card background color
    static let cardBackground = Color.adaptiveColor(
        light: Color.white,
        dark: Color(hex: "1C1C1E")
    )
    
    /// Secondary card background
    static let cardBackgroundSecondary = Color.adaptiveColor(
        light: Color(hex: "F3F4F6"),
        dark: Color(hex: "2C2C2E")
    )
    
    /// Primary text color
    static let textPrimary = Color.adaptiveColor(
        light: Color(hex: "111827"),
        dark: Color(hex: "F9FAFB")
    )
    
    /// Secondary text color
    static let textSecondary = Color.adaptiveColor(
        light: Color(hex: "6B7280"),
        dark: Color(hex: "9CA3AF")
    )
    
    /// Tertiary text color
    static let textTertiary = Color.adaptiveColor(
        light: Color(hex: "9CA3AF"),
        dark: Color(hex: "6B7280")
    )
    
    /// Border color
    static let borderColor = Color.adaptiveColor(
        light: Color(hex: "E5E7EB"),
        dark: Color(hex: "3A3A3C")
    )
    
    // MARK: - Gray Scale (Adaptive)
    
    static let gray50 = Color.adaptiveColor(
        light: Color(hex: "F9FAFB"),
        dark: Color(hex: "1C1C1E")
    )
    
    static let gray100 = Color.adaptiveColor(
        light: Color(hex: "F3F4F6"),
        dark: Color(hex: "2C2C2E")
    )
    
    static let gray200 = Color.adaptiveColor(
        light: Color(hex: "E5E7EB"),
        dark: Color(hex: "3A3A3C")
    )
    
    static let gray300 = Color.adaptiveColor(
        light: Color(hex: "D1D5DB"),
        dark: Color(hex: "48484A")
    )
    
    static let gray400 = Color.adaptiveColor(
        light: Color(hex: "9CA3AF"),
        dark: Color(hex: "636366")
    )
    
    static let gray500 = Color.adaptiveColor(
        light: Color(hex: "6B7280"),
        dark: Color(hex: "8E8E93")
    )
    
    static let gray600 = Color.adaptiveColor(
        light: Color(hex: "4B5563"),
        dark: Color(hex: "AEAEB2")
    )
    
    static let gray700 = Color.adaptiveColor(
        light: Color(hex: "374151"),
        dark: Color(hex: "C7C7CC")
    )
    
    static let gray800 = Color.adaptiveColor(
        light: Color(hex: "1F2937"),
        dark: Color(hex: "D1D1D6")
    )
    
    static let gray900 = Color.adaptiveColor(
        light: Color(hex: "111827"),
        dark: Color(hex: "E5E5EA")
    )
    
    // MARK: - Gradient Definitions
    
    /// Primary gradient (Blue to Indigo)
    static let primaryGradient = LinearGradient(
        colors: [Color(hex: "3B82F6"), Color(hex: "6366F1")],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Primary gradient for dark mode
    static let primaryGradientDark = LinearGradient(
        colors: [Color(hex: "60A5FA"), Color(hex: "818CF8")],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Success gradient (Green variations)
    static let successGradient = LinearGradient(
        colors: [Color(hex: "10B981"), Color(hex: "059669")],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Danger gradient (Red variations)
    static let dangerGradient = LinearGradient(
        colors: [Color(hex: "EF4444"), Color(hex: "DC2626")],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Warning gradient (Orange variations)
    static let warningGradient = LinearGradient(
        colors: [Color(hex: "F59E0B"), Color(hex: "D97706")],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Subtle background gradient
    static let subtleBackgroundGradient = LinearGradient(
        colors: [
            Color(hex: "F9FAFB"),
            Color(hex: "F3F4F6")
        ],
        startPoint: .top,
        endPoint: .bottom
    )
    
    /// Glass overlay gradient (for glass effect)
    static let glassOverlayGradient = LinearGradient(
        colors: [
            Color.white.opacity(0.3),
            Color.white.opacity(0.1)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Glass overlay gradient for dark mode
    static let glassOverlayGradientDark = LinearGradient(
        colors: [
            Color.white.opacity(0.15),
            Color.white.opacity(0.05)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    // MARK: - Shadow Colors
    
    /// Neumorphic light shadow
    static let neumorphicLightShadow = Color.adaptiveColor(
        light: Color.white.opacity(0.8),
        dark: Color(hex: "3A3A3C").opacity(0.5)
    )
    
    /// Neumorphic dark shadow
    static let neumorphicDarkShadow = Color.adaptiveColor(
        light: Color.black.opacity(0.2),
        dark: Color.black.opacity(0.8)
    )
    
    /// Soft shadow for cards
    static let cardShadow = Color.adaptiveColor(
        light: Color.black.opacity(0.08),
        dark: Color.black.opacity(0.4)
    )
    
    // MARK: - Helper Methods
    
    /// Creates an adaptive color that changes based on light/dark mode
    ///
    /// - Parameters:
    ///   - light: Color for light mode
    ///   - dark: Color for dark mode
    /// - Returns: Adaptive Color
    static func adaptiveColor(light: Color, dark: Color) -> Color {
        Color(UIColor { traitCollection in
            traitCollection.userInterfaceStyle == .dark ? UIColor(dark) : UIColor(light)
        })
    }
    
    // MARK: - Hex Initializer
    
    /// Creates a Color from a hex string
    ///
    /// - Parameter hex: Hex color string (e.g., "FF0000" or "#FF0000")
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Gradient Extensions

extension LinearGradient {
    /// Returns appropriate gradient for current color scheme
    ///
    /// - Parameters:
    ///   - light: Gradient for light mode
    ///   - dark: Gradient for dark mode
    ///   - colorScheme: Current color scheme
    /// - Returns: Appropriate gradient
    static func adaptive(light: LinearGradient, dark: LinearGradient, for colorScheme: ColorScheme) -> LinearGradient {
        colorScheme == .dark ? dark : light
    }
}

