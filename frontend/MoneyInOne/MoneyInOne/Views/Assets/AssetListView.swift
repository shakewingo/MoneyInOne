//
//  AssetListView.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/2.
//

import SwiftUI

/// Main asset list view with grouped sections and CRUD operations
struct AssetListView: View {
    // MARK: - Environment
    
    @Environment(AppCoordinator.self) private var coordinator
    
    // MARK: - State
    
    @State private var viewModel = AssetListViewModel()
    @State private var showDeleteAlert = false
    @State private var assetToDelete: Asset?
    @State private var presentedFormMode: FormMode?
    
    // MARK: - Body
    
    var body: some View {
        NavigationStack {
            ZStack {
                if viewModel.isLoading && viewModel.groupedAssets.isEmpty {
                    // Initial loading state
                    LoadingView()
                } else if let errorMessage = viewModel.errorMessage, viewModel.groupedAssets.isEmpty {
                    // Error state
                    ErrorView(
                        error: NSError(domain: "AssetListView", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage]),
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
                        icon: "wallet.pass.fill",
                        title: "No Assets Yet",
                        message: "Start tracking your wealth by adding your first asset",
                        actionTitle: "Add Asset",
                        action: {
                            presentedFormMode = .addAsset
                        }
                    )
                } else {
                    // Assets list
                    assetsList
                }
            }
            .background(Color.appBackground)
            .navigationTitle("Assets")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        presentedFormMode = .addAsset
                    } label: {
                        Image(systemName: "plus")
                            .fontWeight(.semibold)
                    }
                }
                
                ToolbarItem(placement: .navigationBarLeading) {
                    CurrencyPickerMenu()
                }
            }
            .alert("Delete Asset?", isPresented: $showDeleteAlert, presenting: assetToDelete) { asset in
                Button("Cancel", role: .cancel) {
                    assetToDelete = nil
                }
                Button("Delete", role: .destructive) {
                    confirmDelete(asset)
                }
            } message: { asset in
                Text("Are you sure you want to delete '\(asset.name)'? This action will permanently remove the record.")
            }
            .onAppear {
                if viewModel.groupedAssets.isEmpty {
                    viewModel.loadAssets(
                        deviceId: coordinator.deviceID,
                        baseCurrency: coordinator.baseCurrency.rawValue
                    )
                }
            }
            .onChange(of: coordinator.baseCurrency) { _, newCurrency in
                print("💱 AssetListView: Currency changed to \(newCurrency.rawValue), reloading...")
                viewModel.loadAssets(
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
                    viewModel.loadAssets(
                        deviceId: coordinator.deviceID,
                        baseCurrency: coordinator.baseCurrency.rawValue
                    )
                }
            }
        }
    }
    
    // MARK: - Assets List
    
    private var assetsList: some View {
        List {
            ForEach(viewModel.sortedCategories) { category in
                Section {
                    ForEach(viewModel.assets(for: category)) { asset in
                        AssetListRowView(asset: asset)
                            .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                                // Edit action (right-to-left swipe)
                                Button {
                                    HapticFeedback.light()
                                    presentedFormMode = .editAsset(asset)
                                } label: {
                                    Label("Edit", systemImage: "pencil")
                                }
                                .tint(.blue)
                                
                                // Delete action (further right-to-left swipe)
                                Button(role: .destructive) {
                                    HapticFeedback.light()
                                    assetToDelete = asset
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
    
    private func categoryHeader(_ category: AssetCategory) -> some View {
        HStack(spacing: 8) {
            Image(systemName: category.iconName)
                .font(.headline)
                .foregroundColor(category.color)
            
            Text(category.displayName)
                .font(.headline)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text("\(viewModel.count(for: category)) records")
                .font(.caption)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color(.systemGray5))
                .cornerRadius(8)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }
    
    // MARK: - Actions
    
    private func confirmDelete(_ asset: Asset) {
        Task {
            await viewModel.deleteAsset(
                assetId: asset.id,
                deviceId: coordinator.deviceID,
                baseCurrency: coordinator.baseCurrency.rawValue
            )
            assetToDelete = nil
        }
    }
}

// MARK: - Preview

#Preview {
    AssetListView()
        .environment(AppCoordinator())
}

