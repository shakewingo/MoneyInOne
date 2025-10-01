import SwiftUI

struct OnboardingView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var selectedCurrency: Currency = .CNY
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            // Welcome section
            Image(systemName: "chart.pie.fill")
                .font(.system(size: 80))
                .foregroundColor(.primaryColor)
            
            Text("Welcome to MoneyInOne")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Track all your wealth in one place")
                .font(.title3)
                .foregroundColor(.gray600)
                .multilineTextAlignment(.center)
            
            Spacer()
            
            // Currency selection
            VStack(alignment: .leading, spacing: 12) {
                Text("Select Base Currency")
                    .font(.headline)
                
                Picker("Currency", selection: $selectedCurrency) {
                    ForEach(Currency.allCases) { currency in
                        Text("\(currency.symbol) \(currency.rawValue)")
                            .tag(currency)
                    }
                }
                .pickerStyle(.wheel)
                .frame(height: 150)
            }
            .padding()
            .background(Color.gray100)
            .cornerRadius(16)
            
            Spacer()
            
            // Get started button
            Button(action: {
                coordinator.updateBaseCurrency(selectedCurrency)
                coordinator.markOnboardingComplete()
            }) {
                Text("Get Started")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.primaryColor)
                    .cornerRadius(12)
            }
        }
        .padding()
    }
}
