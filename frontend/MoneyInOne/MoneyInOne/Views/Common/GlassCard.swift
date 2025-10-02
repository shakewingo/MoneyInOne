//
//  GlassCard.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//  UI Modernization - Glass/Neumorphic Card Component
//

import SwiftUI

/// A modern glass-effect card with neumorphic styling
///
/// Features:
/// - Frosted glass background with material effect
/// - Layered shadows for depth
/// - Adaptive to light/dark mode
/// - Optional gradient overlay
/// - Smooth rounded corners
struct GlassCard<Content: View>: View {
    // MARK: - Properties
    
    let content: Content
    let style: GlassCardStyle
    let shadowStyle: ShadowStyle
    
    @Environment(\.colorScheme) private var colorScheme
    
    // MARK: - Initialization
    
    /// Creates a glass card with custom styling
    ///
    /// - Parameters:
    ///   - style: Visual style of the card (default: .standard)
    ///   - shadowStyle: Shadow appearance (default: .soft)
    ///   - content: Card content builder
    init(
        style: GlassCardStyle = .standard,
        shadowStyle: ShadowStyle = .soft,
        @ViewBuilder content: () -> Content
    ) {
        self.style = style
        self.shadowStyle = shadowStyle
        self.content = content()
    }
    
    // MARK: - Body
    
    var body: some View {
        content
            .padding(style.padding)
            .background(backgroundView)
            .cornerRadius(style.cornerRadius)
            .overlay(
                RoundedRectangle(cornerRadius: style.cornerRadius)
                    .stroke(borderColor, lineWidth: style.borderWidth)
            )
            .applyShadow(shadowStyle, colorScheme: colorScheme)
    }
    
    // MARK: - Background View
    
    @ViewBuilder
    private var backgroundView: some View {
        ZStack {
            // Base material
            baseMaterial
            
            // Gradient overlay (optional)
            if style.hasGradientOverlay {
                gradientOverlay
            }
        }
    }
    
    private var baseMaterial: some View {
        Group {
            switch style.material {
            case .ultraThin:
                Rectangle()
                    .fill(.ultraThinMaterial)
            case .thin:
                Rectangle()
                    .fill(.thinMaterial)
            case .regular:
                Rectangle()
                    .fill(.regularMaterial)
            case .thick:
                Rectangle()
                    .fill(.thickMaterial)
            case .solid:
                Color.cardBackground
            }
        }
    }
    
    private var gradientOverlay: some View {
        (colorScheme == .dark ? Color.glassOverlayGradientDark : Color.glassOverlayGradient)
            .opacity(style.gradientOpacity)
    }
    
    private var borderColor: Color {
        colorScheme == .dark
            ? Color.white.opacity(0.15)
            : Color.white.opacity(0.6)
    }
}

// MARK: - Glass Card Style

/// Visual style configuration for glass cards
enum GlassCardStyle {
    case standard
    case compact
    case prominent
    case neumorphic
    
    var cornerRadius: CGFloat {
        switch self {
        case .standard: return 16
        case .compact: return 12
        case .prominent: return 20
        case .neumorphic: return 16
        }
    }
    
    var padding: CGFloat {
        switch self {
        case .standard: return 20
        case .compact: return 16
        case .prominent: return 24
        case .neumorphic: return 20
        }
    }
    
    var material: MaterialType {
        switch self {
        case .standard: return .thin
        case .compact: return .ultraThin
        case .prominent: return .regular
        case .neumorphic: return .solid
        }
    }
    
    var hasGradientOverlay: Bool {
        switch self {
        case .standard, .prominent: return true
        case .compact, .neumorphic: return false
        }
    }
    
    var gradientOpacity: Double {
        switch self {
        case .standard: return 0.5
        case .prominent: return 0.7
        default: return 0
        }
    }
    
    var borderWidth: CGFloat {
        switch self {
        case .standard, .compact, .prominent: return 1
        case .neumorphic: return 0
        }
    }
}

// MARK: - Material Type

enum MaterialType {
    case ultraThin
    case thin
    case regular
    case thick
    case solid
}

// MARK: - Shadow Style

/// Shadow configuration for cards
enum ShadowStyle {
    case none
    case soft
    case prominent
    case neumorphic
    
    var shadows: [(color: Color, radius: CGFloat, x: CGFloat, y: CGFloat)] {
        switch self {
        case .none:
            return []
        case .soft:
            return [
                (Color.cardShadow, 10, 0, 2),
                (Color.cardShadow.opacity(0.5), 20, 0, 8)
            ]
        case .prominent:
            return [
                (Color.cardShadow, 15, 0, 5),
                (Color.cardShadow.opacity(0.6), 30, 0, 15)
            ]
        case .neumorphic:
            return [
                (Color.neumorphicDarkShadow, 10, 5, 5),
                (Color.neumorphicLightShadow, 10, -5, -5)
            ]
        }
    }
}

// MARK: - Shadow Modifier

private struct ShadowModifier: ViewModifier {
    let shadowStyle: ShadowStyle
    let colorScheme: ColorScheme
    
    func body(content: Content) -> some View {
        var view = AnyView(content)
        
        for shadow in shadowStyle.shadows {
            view = AnyView(
                view.shadow(
                    color: shadow.color,
                    radius: shadow.radius,
                    x: shadow.x,
                    y: shadow.y
                )
            )
        }
        
        return view
    }
}

private extension View {
    func applyShadow(_ style: ShadowStyle, colorScheme: ColorScheme) -> some View {
        modifier(ShadowModifier(shadowStyle: style, colorScheme: colorScheme))
    }
}

// MARK: - Preview

#Preview("Glass Card Styles") {
    ScrollView {
        VStack(spacing: 24) {
            GlassCard(style: .standard) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Standard Glass Card")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Frosted glass with thin material")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            GlassCard(style: .compact, shadowStyle: .soft) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Compact Glass Card")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Smaller padding, ultra-thin material")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            GlassCard(style: .prominent, shadowStyle: .prominent) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Prominent Glass Card")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Larger corners, stronger shadows")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            GlassCard(style: .neumorphic, shadowStyle: .neumorphic) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Neumorphic Card")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Soft UI with dual shadows")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .padding()
    }
    .background(Color.appBackground)
}

#Preview("Dark Mode") {
    ScrollView {
        VStack(spacing: 24) {
            GlassCard(style: .standard) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Glass Card in Dark Mode")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Materials automatically adapt")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            GlassCard(style: .neumorphic, shadowStyle: .neumorphic) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Neumorphic in Dark")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text("Soft shadows adjust to theme")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .padding()
    }
    .background(Color.appBackground)
    .preferredColorScheme(.dark)
}

