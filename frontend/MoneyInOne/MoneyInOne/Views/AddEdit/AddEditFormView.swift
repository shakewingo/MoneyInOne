//
//  AddEditFormView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Unified form view for adding and editing assets and credits
struct AddEditFormView: View {
    // MARK: - Environment
    
    @Environment(\.dismiss) private var dismiss
    @Environment(AppCoordinator.self) private var coordinator
    
    // MARK: - State
    
    @State private var viewModel: AddEditViewModel
    @State private var showSuccessAlert = false
    
    // MARK: - Initialization
    
    init(mode: FormMode) {
        self._viewModel = State(initialValue: AddEditViewModel(mode: mode))
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Modern background
            Color.appBackground
                .ignoresSafeArea()
            
            Form {
                // Category Section
                categorySection
                
                // Basic Information Section
                basicInfoSection
                
                // Stock-specific fields (conditional)
                if viewModel.requiresStockFields {
                    stockFieldsSection
                }
                
                // Notes Section
                notesSection
            }
            .scrollContentBackground(.hidden)
            .navigationTitle(viewModel.mode.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .confirmationAction) {
                    Button(viewModel.mode.saveButtonTitle) {
                        handleSave()
                    }
                    .disabled(viewModel.isLoading)
                }
            }
            .alert("Success!", isPresented: $showSuccessAlert) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text(viewModel.mode.isEditMode ? "Updated successfully!" : "Created successfully!")
            }
            
            // Loading overlay
            if viewModel.isLoading {
                Color.black.opacity(0.3)
                    .ignoresSafeArea()
                
                ProgressView()
                    .scaleEffect(1.5)
                    .tint(.white)
            }
        }
    }
    
    // MARK: - Category Section
    
    private var categorySection: some View {
        Section {
            if viewModel.isAssetMode {
                Picker("Category", selection: $viewModel.selectedAssetCategory) {
                    ForEach(AssetCategory.allCases) { category in
                        Label(category.displayName, systemImage: category.iconName)
                            .tag(category)
                    }
                }
                .onChange(of: viewModel.selectedAssetCategory) { _, newValue in
                    switch newValue {
                    case .gold:
                        viewModel.symbol = "GLD"
                        viewModel.currency = .USD
                    case .silver:
                        viewModel.symbol = "SLV"
                        viewModel.currency = .USD
                    case .stock, .crypto:
                        viewModel.symbol = "" 
                        viewModel.currency = .USD
                    default:
                        // Ensure auto-filled GLD/SLV doesn't persist when switching to other categories
                        if viewModel.symbol == "GLD" || viewModel.symbol == "SLV" { viewModel.symbol = "" }
                        break
                    }
                }
                if viewModel.selectedAssetCategory == .stock || viewModel.selectedAssetCategory == .crypto ||
                    viewModel.selectedAssetCategory == .gold || viewModel.selectedAssetCategory == .silver {
                    HStack(spacing: 6) {
                        Image(systemName: "info.circle")
                        Text("For stock/crypto/precious metals, support tracking based on USD only.")
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
            } else {
                Picker("Category", selection: $viewModel.selectedCreditCategory) {
                    ForEach(CreditCategory.allCases) { category in
                        Label(category.displayName, systemImage: category.iconName)
                            .tag(category)
                    }
                }
            }
        } header: {
            Text("Category")
        }
    }
    
    // MARK: - Basic Info Section
    
    private var basicInfoSection: some View {
        Section {
            // Name
            VStack(alignment: .leading, spacing: 4) {
                TextField("Name", text: $viewModel.name)
                if let error = viewModel.validationErrors["name"] {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            
            // Currency (auto USD for stock/crypto/gold/silver)
            if viewModel.isAssetMode && (viewModel.selectedAssetCategory == .stock || viewModel.selectedAssetCategory == .crypto || viewModel.selectedAssetCategory == .gold || viewModel.selectedAssetCategory == .silver) {
                HStack {
                    Text("Currency")
                    Spacer()
                    Text("USD").foregroundColor(.secondary)
                }
            } else {
                CurrencyPickerView(selectedCurrency: $viewModel.currency)
            }
            
            // Amount
            VStack(alignment: .leading, spacing: 4) {
                AmountTextField(
                    amount: $viewModel.amount,
                    currencySymbol: viewModel.currency.symbol,
                    placeholder: "0.00"
                )
                if let error = viewModel.validationErrors["amount"] {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            
            // Date
            DatePicker(
                viewModel.dateLabel,
                selection: $viewModel.date,
                displayedComponents: .date
            )
        } header: {
            Text("Basic Information")
        }
    }
    
    // MARK: - Stock Fields Section
    
    private var stockFieldsSection: some View {
        Section {
            // Symbol
            VStack(alignment: .leading, spacing: 4) {
                TextField("Symbol (e.g., AAPL, BTC)", text: $viewModel.symbol)
                    .textInputAutocapitalization(.characters)
                if let error = viewModel.validationErrors["symbol"] {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            
            // Shares
            VStack(alignment: .leading, spacing: 4) {
                TextField(
                    (viewModel.selectedAssetCategory == .gold || viewModel.selectedAssetCategory == .silver)
                    ? "Ounces (oz)"
                    : "Number of Shares",
                    text: $viewModel.shares
                )
                    .keyboardType(.decimalPad)
                if let error = viewModel.validationErrors["shares"] {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            
            // Track Market Value Toggle
            Toggle("Track Market Value", isOn: $viewModel.isMarketTracked)
        } header: {
            Text("Details")
        } footer: {
            HStack(spacing: 6) {
                Image(systemName: "info.circle")
                Text("Enable market tracking to automatically update prices. (Recommended)")
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
    }
    
    // MARK: - Notes Section
    
    private var notesSection: some View {
        Section {
            TextField(
                "Notes (optional)",
                text: $viewModel.notes,
                axis: .vertical
            )
            .lineLimit(3...6)
        } header: {
            Text("Additional Information")
        }
    }
    
    // MARK: - Actions
    
    private func handleSave() {
        Task {
            do {
                try await viewModel.submitForm(deviceId: coordinator.deviceID)
                
                // Show success alert
                await MainActor.run {
                    showSuccessAlert = true
                }
                
                // Auto-dismiss after 1 second
                try await Task.sleep(nanoseconds: 1_000_000_000)
                await MainActor.run {
                    dismiss()
                }
            } catch {
                print("❌ Failed to save: \(error)")
                // Error is displayed via viewModel.errorMessage
            }
        }
    }
}

// MARK: - Preview

#Preview("Add Asset") {
    NavigationStack {
        AddEditFormView(mode: .addAsset)
    }
    .environment(AppCoordinator())
}

#Preview("Edit Asset") {
    let sampleAsset = Asset(
        id: UUID(),
        userId: UUID(),
        name: "Apple Inc.",
        category: .stock,
        amount: 28950.00,
        currency: "USD",
        purchaseDate: Date(),
        notes: "Tech investment",
        symbol: "AAPL",
        shares: 150,
        
        lastPriceUpdate: Date(),
        isMarketTracked: true,
        convertedAmount: 28950.00,
        conversionRate: 1.0,
        createdAt: Date(),
        updatedAt: Date()
    )
    
    return NavigationStack {
        AddEditFormView(mode: .editAsset(sampleAsset))
    }
    .environment(AppCoordinator())
}

#Preview("Add Credit") {
    NavigationStack {
        AddEditFormView(mode: .addCredit)
    }
    .environment(AppCoordinator())
}

