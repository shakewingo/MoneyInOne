//
//  CreditListView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Main credit list view with grouped sections and CRUD operations
struct CreditListView: View {
    // MARK: - Environment
    
    @Environment(AppCoordinator.self) private var coordinator
    
    // MARK: - State
    
    @State private var viewModel = CreditListViewModel()
    @State private var showDeleteAlert = false
    @State private var creditToDelete: Credit?
    @State private var presentedFormMode: FormMode?
    
    // MARK: - Body
    
    var body: some View {
        NavigationStack {
            ZStack {
                if viewModel.isLoading && viewModel.groupedCredits.isEmpty {
                    // Initial loading state
                    LoadingView()
                } else if let errorMessage = viewModel.errorMessage, viewModel.groupedCredits.isEmpty {
                    // Error state
                    ErrorView(
                        error: NSError(domain: "CreditListView", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage]),
                        retryAction: {
                            viewModel.retryLoad(
                                deviceId: coordinator.deviceID,
                                baseCurrency: coordinator.baseCurrency.rawValue
                            )
                        }
                    )
                } else if viewModel.isEmpty {
                    // Empty state
                    EmptyStateView(
                        icon: "creditcard.fill",
                        title: "No Credits Yet",
                        message: "Start tracking your debts and obligations by adding your first credit",
                        actionTitle: "Add Credit",
                        action: {
                            presentedFormMode = .addCredit
                        }
                    )
                } else {
                    // Credits list
                    creditsList
                }
            }
            .background(Color.appBackground)
            .navigationTitle("Credits")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        presentedFormMode = .addCredit
                    } label: {
                        Image(systemName: "plus")
                            .fontWeight(.semibold)
                    }
                }
                
                ToolbarItem(placement: .navigationBarLeading) {
                    CurrencyPickerMenu()
                }
            }
            .alert("Delete Credit?", isPresented: $showDeleteAlert, presenting: creditToDelete) { credit in
                Button("Cancel", role: .cancel) {
                    creditToDelete = nil
                }
                Button("Delete", role: .destructive) {
                    confirmDelete(credit)
                }
            } message: { credit in
                Text("Are you sure you want to delete '\(credit.name)'? This action will permanently remove the record.")
            }
            .onAppear {
                if viewModel.groupedCredits.isEmpty {
                    viewModel.loadCredits(
                        deviceId: coordinator.deviceID,
                        baseCurrency: coordinator.baseCurrency.rawValue
                    )
                }
            }
            .onChange(of: coordinator.baseCurrency) { _, newCurrency in
                print("💱 CreditListView: Currency changed to \(newCurrency.rawValue), reloading...")
                viewModel.loadCredits(
                    deviceId: coordinator.deviceID,
                    baseCurrency: newCurrency.rawValue
                )
            }
            .sheet(item: $presentedFormMode) { mode in
                NavigationStack {
                    AddEditFormView(mode: mode)
                }
                .presentationDetents([.large])
                .onDisappear {
                    // Refresh list when form dismisses
                    viewModel.loadCredits(
                        deviceId: coordinator.deviceID,
                        baseCurrency: coordinator.baseCurrency.rawValue
                    )
                }
            }
        }
    }
    
    // MARK: - Credits List
    
    private var creditsList: some View {
        List {
            ForEach(viewModel.sortedCategories) { category in
                Section {
                    ForEach(viewModel.credits(for: category)) { credit in
                        CreditListRowView(credit: credit)
                            .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                                // Edit action (right-to-left swipe)
                                Button {
                                    HapticFeedback.light()
                                    presentedFormMode = .editCredit(credit)
                                } label: {
                                    Label("Edit", systemImage: "pencil")
                                }
                                .tint(.blue)
                                
                                // Delete action (right-to-left swipe)
                                Button(role: .destructive) {
                                    HapticFeedback.light()
                                    creditToDelete = credit
                                    showDeleteAlert = true
                                } label: {
                                    Label("Delete", systemImage: "trash")
                                }
                            }
                    }
                } header: {
                    categoryHeader(category)
                }
            }
        }
        .listStyle(.insetGrouped)
        .refreshable {
            await viewModel.refresh(
                deviceId: coordinator.deviceID,
                baseCurrency: coordinator.baseCurrency.rawValue
            )
        }
    }
    
    // MARK: - Category Header
    
    private func categoryHeader(_ category: CreditCategory) -> some View {
        HStack(spacing: 8) {
            Image(systemName: category.iconName)
                .font(.headline)
                .foregroundColor(category.color)
            
            Text(category.displayName)
                .font(.headline)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(viewModel.count(for: category) == 1 ? "1 item" : "\(viewModel.count(for: category)) items")
                .font(.caption)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color(.systemGray5))
                .cornerRadius(8)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
        .textCase(nil)  // Prevent automatic uppercasing by iOS List section headers
    }
    
    // MARK: - Actions
    
    private func confirmDelete(_ credit: Credit) {
        Task {
            await viewModel.deleteCredit(
                creditId: credit.id,
                deviceId: coordinator.deviceID,
                baseCurrency: coordinator.baseCurrency.rawValue
            )
            creditToDelete = nil
        }
    }
}

// MARK: - Preview

#Preview {
    CreditListView()
        .environment(AppCoordinator())
}

