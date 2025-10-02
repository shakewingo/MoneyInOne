//
//  ViewModifiers.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//  UI Modernization - Animations and Micro-Interactions
//

import SwiftUI

// MARK: - Button Press Animation

struct ButtonPressAnimation: ViewModifier {
    @State private var isPressed = false
    
    func body(content: Content) -> some View {
        content
            .scaleEffect(isPressed ? 0.96 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isPressed)
            .simultaneousGesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { _ in
                        if !isPressed {
                            isPressed = true
                            hapticFeedback(style: .light)
                        }
                    }
                    .onEnded { _ in
                        isPressed = false
                    }
            )
    }
    
    private func hapticFeedback(style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
}

extension View {
    /// Adds a spring-based press animation with haptic feedback
    func buttonPressAnimation() -> some View {
        modifier(ButtonPressAnimation())
    }
}

// MARK: - Haptic Feedback Helper

struct HapticFeedback {
    /// Light tap feedback (for selection)
    static func light() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
    }
    
    /// Medium tap feedback (for button press)
    static func medium() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }
    
    /// Heavy tap feedback (for important actions)
    static func heavy() {
        let generator = UIImpactFeedbackGenerator(style: .heavy)
        generator.impactOccurred()
    }
    
    /// Success notification feedback
    static func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }
    
    /// Error notification feedback
    static func error() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.error)
    }
    
    /// Warning notification feedback
    static func warning() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.warning)
    }
}

// MARK: - Shimmer Effect (for loading states)

struct ShimmerEffect: ViewModifier {
    @State private var isAnimating = false
    
    func body(content: Content) -> some View {
        content
            .overlay(
                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(0),
                                Color.white.opacity(0.3),
                                Color.white.opacity(0)
                            ],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .rotationEffect(.degrees(30))
                    .offset(x: isAnimating ? 300 : -300)
            )
            .clipped()
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    isAnimating = true
                }
            }
    }
}

extension View {
    /// Adds a shimmer loading effect
    func shimmer() -> some View {
        modifier(ShimmerEffect())
    }
}

// MARK: - Skeleton Loading

struct SkeletonView: View {
    var body: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(Color.gray300)
            .shimmer()
    }
}

// MARK: - Card Appear Animation

struct CardAppearAnimation: ViewModifier {
    @State private var isVisible = false
    let delay: Double
    
    func body(content: Content) -> some View {
        content
            .opacity(isVisible ? 1 : 0)
            .offset(y: isVisible ? 0 : 20)
            .onAppear {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.8).delay(delay)) {
                    isVisible = true
                }
            }
    }
}

extension View {
    /// Animates card appearance with a spring effect
    ///
    /// - Parameter delay: Animation delay in seconds
    func cardAppear(delay: Double = 0) -> some View {
        modifier(CardAppearAnimation(delay: delay))
    }
}

// MARK: - Bounce Animation

struct BounceAnimation: ViewModifier {
    @State private var isAnimating = false
    
    func body(content: Content) -> some View {
        content
            .scaleEffect(isAnimating ? 1.1 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.5), value: isAnimating)
            .onAppear {
                isAnimating = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                    isAnimating = false
                }
            }
    }
}

extension View {
    /// Adds a quick bounce animation on appear
    func bounce() -> some View {
        modifier(BounceAnimation())
    }
}

// MARK: - Hover Effect (for interactive elements)

struct HoverEffect: ViewModifier {
    @State private var isHovered = false
    
    func body(content: Content) -> some View {
        content
            .scaleEffect(isHovered ? 1.05 : 1.0)
            .shadow(
                color: Color.cardShadow.opacity(isHovered ? 0.3 : 0.1),
                radius: isHovered ? 12 : 6,
                x: 0,
                y: isHovered ? 8 : 4
            )
            .animation(.spring(response: 0.4, dampingFraction: 0.7), value: isHovered)
            .onLongPressGesture(minimumDuration: 0.0, maximumDistance: .infinity, pressing: { pressing in
                isHovered = pressing
            }, perform: {})
    }
}

extension View {
    /// Adds a hover/press scale effect with shadow
    func hoverEffect() -> some View {
        modifier(HoverEffect())
    }
}

// MARK: - Slide In Animation

struct SlideInAnimation: ViewModifier {
    enum Direction {
        case leading, trailing, top, bottom
    }
    
    @State private var isVisible = false
    let direction: Direction
    let delay: Double
    
    func body(content: Content) -> some View {
        content
            .opacity(isVisible ? 1 : 0)
            .offset(
                x: isVisible ? 0 : offsetX,
                y: isVisible ? 0 : offsetY
            )
            .onAppear {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.8).delay(delay)) {
                    isVisible = true
                }
            }
    }
    
    private var offsetX: CGFloat {
        switch direction {
        case .leading: return -100
        case .trailing: return 100
        default: return 0
        }
    }
    
    private var offsetY: CGFloat {
        switch direction {
        case .top: return -100
        case .bottom: return 100
        default: return 0
        }
    }
}

extension View {
    /// Animates view sliding in from a direction
    ///
    /// - Parameters:
    ///   - direction: Direction to slide from
    ///   - delay: Animation delay in seconds
    func slideIn(from direction: SlideInAnimation.Direction = .bottom, delay: Double = 0) -> some View {
        modifier(SlideInAnimation(direction: direction, delay: delay))
    }
}

// MARK: - Success Checkmark Animation

struct SuccessCheckmark: View {
    @State private var isAnimating = false
    
    var body: some View {
        ZStack {
            Circle()
                .fill(Color.successColor)
                .frame(width: 60, height: 60)
                .scaleEffect(isAnimating ? 1 : 0)
            
            Image(systemName: "checkmark")
                .font(.system(size: 30, weight: .bold))
                .foregroundColor(.white)
                .scaleEffect(isAnimating ? 1 : 0)
        }
        .onAppear {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.6)) {
                isAnimating = true
            }
            HapticFeedback.success()
        }
    }
}

