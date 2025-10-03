# MoneyInOne - iOS Frontend Requirements Document

## 1. Project Overview

### 1.1 Application Purpose
MoneyInOne is a financial bookkeeping iOS app that tracks and summarizes all assets (money, stocks, crypto, real estate) and credits (credit cards, loans, mortgages) with multi-currency support and automatic market price updates for stocks and cryptocurrencies.

### 1.2 Core Features
- ✅ Multi-currency asset and credit management (CNY as primary, supports USD, EUR, GBP, JPY, CAD, AUD)
- ✅ Real-time market price updates for stocks and crypto (automatic on app launch)
- ✅ Portfolio dashboard with net worth calculation
- ✅ Full CRUD operations for both assets and credits
- ✅ Category-based grouping and visualization
- ✅ Currency conversion to display unified portfolio value

### 1.3 Design Philosophy
- **Native-first**: Follow iOS Human Interface Guidelines, NOT strict HTML replication
- **Clean & Elegant**: Unified code structure for Assets and Credits (avoid duplication)
- **User-friendly**: Intuitive navigation using SwiftUI NavigationStack, sheets, and forms

---

## 2. Technical Architecture

### 2.1 Tech Stack
- **Language**: Swift 5.9+
- **Framework**: SwiftUI (iOS 17.0+)
- **Architecture**: MVVM with Combine/Observation framework
- **Networking**: URLSession with async/await
- **Data Persistence**: 
  - Keychain (device_id storage)
  - UserDefaults (user preferences like base currency)
- **Dependency Management**: Swift Package Manager (SPM)

### 2.2 Project Structure
```
MoneyInOne/
├── App/
│   ├── MoneyInOneApp.swift          # App entry point
│   └── AppCoordinator.swift         # Device ID management, initialization
├── Models/
│   ├── Asset.swift                  # Asset data model
│   ├── Credit.swift                 # Credit data model
│   ├── Portfolio.swift              # Portfolio summary model
│   ├── Currency.swift               # Currency enum and info
│   └── FinancialItem.swift          # Protocol for Asset/Credit shared behavior
├── ViewModels/
│   ├── DashboardViewModel.swift     # Dashboard logic
│   ├── AssetListViewModel.swift     # Asset list logic
│   ├── CreditListViewModel.swift    # Credit list logic
│   ├── AddEditViewModel.swift       # Shared Add/Edit logic
│   └── PortfolioViewModel.swift     # Portfolio calculations
├── Views/
│   ├── Dashboard/
│   │   ├── DashboardView.swift
│   │   ├── PortfolioSummaryCard.swift
│   │   ├── AssetBreakdownChart.swift
│   │   └── TopAssetsSection.swift
│   ├── Assets/
│   │   ├── AssetListView.swift
│   │   └── AssetRowView.swift
│   ├── Credits/
│   │   ├── CreditListView.swift
│   │   └── CreditRowView.swift
│   ├── AddEdit/
│   │   ├── AddEditItemView.swift    # Generic add/edit view
│   │   └── FormComponents/
│   │       ├── CategoryPicker.swift
│   │       ├── CurrencyPicker.swift
│   │       ├── DatePicker.swift
│   │       └── AmountTextField.swift
│   └── Common/
│       ├── LoadingView.swift
│       ├── ErrorView.swift
│       └── EmptyStateView.swift
├── Services/
│   ├── APIService.swift             # Base API communication
│   ├── AssetService.swift           # Asset endpoints
│   ├── CreditService.swift          # Credit endpoints
│   ├── PortfolioService.swift       # Portfolio endpoints
│   ├── MetadataService.swift        # Metadata endpoints
│   └── MarketDataService.swift      # Market data refresh
├── Utilities/
│   ├── DeviceIDManager.swift        # Keychain management
│   ├── CurrencyFormatter.swift      # Currency display formatting
│   ├── DateFormatter+Extensions.swift
│   └── Color+Theme.swift            # Color theme
└── Resources/
    └── Assets.xcassets              # Icons, colors
```

### 2.3 Device ID Management
- Generate UUID on first app launch
- Store in Keychain (secure, persists across app reinstalls)
- Pass as `X-Device-ID` header or `device_id` query parameter in all API calls

### 2.4 State Management
- Use `@Observable` macro (iOS 17+) for ViewModels
- `@State` and `@Binding` for local view state
- Combine publishers for async data streams

---

## 3. Backend API Integration

### 3.1 Base Configuration
```swift
struct APIConfig {
    static let baseURL = "http://localhost:8000/api/v1"
    static let timeout: TimeInterval = 30
}
```

### 3.2 API Endpoints

#### 3.2.1 Assets
- `POST /assets` - Create asset
- `GET /assets?device_id={id}&base_currency={currency}` - Get all assets grouped by category
- `GET /assets/{asset_id}?device_id={id}` - Get single asset
- `PUT /assets/{asset_id}?device_id={id}` - Update asset
- `DELETE /assets/{asset_id}?device_id={id}` - Delete asset
- `POST /assets/refresh-prices` (Header: X-Device-ID) - Refresh all market prices

#### 3.2.2 Credits
- `POST /credits` - Create credit
- `GET /credits?device_id={id}&base_currency={currency}` - Get all credits grouped by category
- `GET /credits/{credit_id}?device_id={id}` - Get single credit
- `PUT /credits/{credit_id}?device_id={id}` - Update credit
- `DELETE /credits/{credit_id}?device_id={id}` - Delete credit

#### 3.2.3 Portfolio
- `GET /portfolio/summary?device_id={id}&base_currency={currency}` - Get portfolio summary

#### 3.2.4 Metadata
- `GET /metadata` - Get currencies, asset categories, credit categories
- `GET /metadata/currencies` - Get currency list
- `GET /metadata/asset-categories` - Get asset category list
- `GET /metadata/credit-categories` - Get credit category list

### 3.3 Request/Response Models

#### Asset Category
```swift
enum AssetCategory: String, Codable, CaseIterable {
    case cash = "cash"
    case stock = "stock"
    case crypto = "crypto"
    case realEstate = "real_estate"
    case bond = "bond"
    case other = "other"
}
```

#### Credit Category
```swift
enum CreditCategory: String, Codable, CaseIterable {
    case creditCard = "credit_card"
    case loan = "loan"
    case mortgage = "mortgage"
    case lineOfCredit = "line_of_credit"
    case other = "other"
}
```

#### Currency
```swift
enum Currency: String, Codable, CaseIterable {
    case CNY = "CNY"  // Primary
    case USD = "USD"
    case EUR = "EUR"
    case GBP = "GBP"
    case JPY = "JPY"
    case CAD = "CAD"
    case AUD = "AUD"
}
```

#### Asset Model
```swift
struct Asset: Identifiable, Codable {
    let id: UUID
    let userId: UUID
    var name: String
    var category: AssetCategory
    var amount: Decimal
    var currency: Currency
    var purchaseDate: Date
    var notes: String?
    var symbol: String?
    var shares: Double?
    var originalAmount: Decimal?
    var currentAmount: Decimal?
    var lastPriceUpdate: Date?
    var isMarketTracked: Bool
    var convertedAmount: Decimal?
    var conversionRate: Decimal?
    let createdAt: Date
    let updatedAt: Date
}
```

#### Credit Model
```swift
struct Credit: Identifiable, Codable {
    let id: UUID
    let userId: UUID
    var name: String
    var category: CreditCategory
    var amount: Decimal
    var currency: Currency
    var issueDate: Date
    var notes: String?
    var convertedAmount: Decimal?
    var conversionRate: Decimal?
    let createdAt: Date
    let updatedAt: Date
}
```

---

## 4. Development Plan (Phased Approach)

### Phase 0: Project Setup & Infrastructure (Day 1)
**Goal**: Create project foundation with API integration and device management

#### Tasks:
1. ✅ Create Xcode project with SwiftUI + iOS 17+
2. ✅ Set up project structure (folders, groups)
3. ✅ Implement `DeviceIDManager` (Keychain storage)
4. ✅ Implement base `APIService` with URLSession
5. ✅ Create data models (Asset, Credit, Portfolio, Currency)
6. ✅ Implement `MetadataService` and load currencies/categories
7. ✅ Create reusable UI components (LoadingView, ErrorView, EmptyStateView)
8. ✅ Set up color theme and basic styling

#### Success Criteria:
- App launches successfully
- Device ID is generated and persisted
- Can successfully call `/metadata` endpoint and receive data
- Basic navigation structure is in place

---

### Phase 1: Dashboard View (Day 2-3)
**Goal**: Build main dashboard with portfolio summary and navigation

#### Tasks:
1. ✅ Create `DashboardView` with TabView/NavigationStack
2. ✅ Implement `PortfolioViewModel` 
   - Fetch portfolio summary
   - Trigger market price refresh on app launch
3. ✅ Build `PortfolioSummaryCard`
   - Total portfolio value
   - Total assets
   - Total credits
   - Net worth
   - Display in selected base currency
4. ✅ Build `AssetBreakdownChart` (simple bar/pie chart)
   - Show asset distribution by category
5. ✅ Build `TopAssetsSection` (list of top 5 assets by value)
6. ✅ Add base currency picker (CNY default)
7. ✅ Implement pull-to-refresh (optional since auto-refresh on launch)
8. ✅ Add navigation to Asset List and Credit List

#### API Integration:
- `GET /portfolio/summary?device_id={id}&base_currency={currency}`
- `POST /assets/refresh-prices` (Header: X-Device-ID) - on app launch

#### Success Criteria:
- Dashboard displays portfolio summary correctly
- Market prices refresh automatically on app launch
- Currency conversion works correctly
- Can navigate to asset and credit lists
- Handles loading and error states gracefully

---

### Phase 2: Asset & Credit List Views (Day 4-5)
**Goal**: Display all assets and credits, grouped by category

#### Tasks:
1. ✅ Create `AssetListView`
   - Group assets by category (cash, stock, crypto, etc.)
   - Display total per category
   - Show count badge
2. ✅ Create `CreditListView`
   - Group credits by category
   - Display total per category
   - Show count badge
3. ✅ Build `AssetRowView` and `CreditRowView`
   - Display name, amount, currency badge
   - Show purchase/issue date
   - Show last updated date
   - Add swipe actions (Edit, Delete)
4. ✅ Implement `AssetListViewModel` and `CreditListViewModel`
   - Fetch grouped data from API
   - Handle currency conversion
5. ✅ Add "+" button to navigate to Add view
6. ✅ Implement tap to navigate to Edit view
7. ✅ Add empty state view when no assets/credits exist

#### API Integration:
- `GET /assets?device_id={id}&base_currency={currency}`
- `GET /credits?device_id={id}&base_currency={currency}`

#### Success Criteria:
- Assets and credits are grouped correctly by category
- List displays all data accurately with proper formatting
- Can navigate to Add/Edit views
- Empty state shows helpful message
- Swipe actions work smoothly

---

### Phase 3: Add/Edit Views (Day 6-8)
**Goal**: Create unified Add/Edit form for both assets and credits

#### Tasks:
1. ✅ Create `AddEditItemView` (generic for Asset AND Credit)
   - Use enum to determine mode: `.addAsset`, `.editAsset`, `.addCredit`, `.editCredit`
2. ✅ Implement `AddEditViewModel`
   - Handle both asset and credit creation/updates
   - Form validation
   - API calls
3. ✅ Build reusable form components:
   - `CategoryPicker` (dynamic based on asset/credit)
   - `CurrencyPicker` (all currencies, CNY default)
   - `DatePicker` (purchase_date or issue_date)
   - `AmountTextField` (with currency symbol)
   - Notes text field
   - **Stock-specific fields** (symbol, shares) - show only when category is "stock"
4. ✅ Add form validation:
   - Name required
   - Amount > 0
   - Category selected
   - Symbol required if category is "stock"
   - Shares required if category is "stock"
5. ✅ Implement save logic
   - Create vs Update based on mode
   - Show loading indicator
   - Handle success/error
   - Navigate back on success
6. ✅ Add "Cancel" and "Save" buttons
7. ✅ Add "Delete" button (only in Edit mode)

#### API Integration:
- `POST /assets` - Create asset
- `PUT /assets/{asset_id}?device_id={id}` - Update asset
- `POST /credits` - Create credit
- `PUT /credits/{credit_id}?device_id={id}` - Update credit

#### Success Criteria:
- Form works for both assets and credits
- Stock-specific fields show/hide based on category
- Validation works correctly
- Can create new assets and credits
- Can edit existing assets and credits
- Data persists correctly on backend
- Error handling is user-friendly

---

### Phase 4: Delete Confirmation (Day 9)
**Goal**: Implement safe delete with confirmation

#### Tasks:
1. ✅ Add delete button in Edit view (bottom of form)
2. ✅ Create confirmation alert/sheet
   - Show item name and amount
   - Warning message: "This action cannot be undone"
   - Cancel and Delete buttons
3. ✅ Implement delete logic in ViewModel
   - Call API
   - Navigate back on success
   - Show error if fails
4. ✅ Alternative: Swipe-to-delete in list views
   - Show confirmation before actual deletion

#### API Integration:
- `DELETE /assets/{asset_id}?device_id={id}` - Delete asset
- `DELETE /credits/{credit_id}?device_id={id}` - Delete credit

#### Success Criteria:
- Delete requires confirmation
- Successfully deletes from backend
- List updates after deletion
- Error handling works correctly

---

### Phase 5: Polish & Testing (Day 10-11)
**Goal**: Refine UI, fix bugs, add final touches

#### Tasks:
1. ✅ UI/UX polish:
   - Consistent spacing and padding
   - Proper color theme (primary: blue, success: green, danger: red)
   - Icon consistency
   - Loading states
   - Error messages
   - Empty states
2. ✅ Currency formatting:
   - Show proper currency symbols (¥, $, €, £, etc.)
   - Number formatting based on locale
3. ✅ Date formatting:
   - Show relative dates ("2 minutes ago", "Dec 15, 2024")
4. ✅ Handle edge cases:
   - Network errors
   - Empty data
   - Invalid inputs
   - Large numbers
5. ✅ Add transitions and animations
6. ✅ Test on different screen sizes (iPhone SE, iPhone 15, iPhone 15 Pro Max)
7. ✅ Performance optimization:
   - Lazy loading for lists
   - Image caching (if needed)
8. ✅ Add accessibility labels
9. ✅ Dark mode support

#### Success Criteria:
- App feels polished and native
- All edge cases handled
- No crashes or UI glitches
- Works on all iPhone sizes
- Smooth animations
- Accessible

---

### Phase 6: Market Data Integration Testing (Day 12)
**Goal**: Ensure automatic price refresh works correctly

#### Tasks:
1. ✅ Test automatic price refresh on app launch
2. ✅ Verify that stock and crypto prices update correctly
3. ✅ Test with different symbols (AAPL, BTC, ETH)
4. ✅ Ensure UI updates after price refresh
5. ✅ Handle cases where symbol is invalid or API fails
6. ✅ Test `last_price_update` timestamp display

#### API Integration:
- `POST /assets/refresh-prices` (Header: X-Device-ID)

#### Success Criteria:
- Prices refresh automatically on app launch
- UI shows updated prices
- Error handling for failed price updates
- Timestamp shows when prices were last updated

---

## 5. Key Technical Considerations

### 5.1 Currency Handling
- Use `Decimal` for all monetary amounts (avoid `Double` for precision)
- Display currency symbols based on currency code
- Support different decimal places (JPY has 0, most others have 2)
- Show conversion rate when displaying converted amounts

### 5.2 Market Data
- Automatically refresh on app launch (no manual button needed)
- Only refresh assets where `is_market_tracked == true`
- Show loading indicator during refresh
- Display last update timestamp
- Handle partial failures gracefully

### 5.3 Error Handling Strategy
```swift
enum APIError: LocalizedError {
    case networkError(Error)
    case invalidResponse
    case serverError(Int, String)
    case decodingError(Error)
    
    var errorDescription: String? {
        switch self {
        case .networkError: return "Network connection failed. Please check your internet."
        case .invalidResponse: return "Invalid response from server."
        case .serverError(_, let message): return message
        case .decodingError: return "Failed to parse response data."
        }
    }
}
```

### 5.4 Date Handling
- Store dates in ISO 8601 format
- Display dates in user's locale
- Show relative dates for recent updates ("2 minutes ago")
- Use standard date picker for purchase/issue dates

### 5.5 Navigation Pattern
```
TabView (Bottom Navigation)
├── Dashboard Tab
│   ├── PortfolioSummaryCard
│   ├── AssetBreakdownChart
│   └── TopAssetsSection
├── Assets Tab
│   ├── AssetListView (grouped by category)
│   │   └── Navigate to AddEditItemView (Edit mode)
│   └── "+" button → AddEditItemView (Add mode)
└── Credits Tab
    ├── CreditListView (grouped by category)
    │   └── Navigate to AddEditItemView (Edit mode)
    └── "+" button → AddEditItemView (Add mode)
```

---

## 6. UI/UX Guidelines

### 6.1 Color Theme
```swift
extension Color {
    static let primary = Color.blue        // #3B82F6
    static let secondary = Color.indigo    // #1E40AF
    static let success = Color.green       // #10B981
    static let danger = Color.red          // #EF4444
    static let warning = Color.orange      // #F59E0B
}
```

### 6.2 Typography
- Use system fonts (San Francisco)
- Large Title for main headers
- Title for section headers
- Body for content
- Caption for metadata (dates, counts)

### 6.3 Icons
- Use SF Symbols for all icons
- Asset categories: 
  - Cash: `dollarsign.circle`
  - Stock: `chart.line.uptrend.xyaxis`
  - Crypto: `bitcoinsign.circle`
  - Real Estate: `house.fill`
  - Bond: `doc.text.fill`
  - Other: `ellipsis.circle`
- Credit categories:
  - Credit Card: `creditcard.fill`
  - Loan: `banknote.fill`
  - Mortgage: `house.and.flag.fill`
  - Line of Credit: `arrow.left.arrow.right`
  - Other: `ellipsis.circle`

### 6.4 Spacing
- Standard padding: 16pt
- Card padding: 20pt
- Section spacing: 24pt
- List item spacing: 12pt

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Test ViewModels in isolation
- Mock API services
- Test business logic (currency conversion, calculations)
- Test validation logic

### 7.2 Integration Tests
- Test API integration with real backend (local)
- Test navigation flows
- Test CRUD operations end-to-end

### 7.3 UI Tests
- Test main user flows:
  - Add asset → View in list → Edit → Delete
  - Add credit → View in list → Edit → Delete
  - View dashboard → Navigate to lists
- Test error states
- Test empty states

### 7.4 Manual Testing Checklist
- [ ] Device ID persists across app launches
- [ ] All CRUD operations work for assets
- [ ] All CRUD operations work for credits
- [ ] Dashboard shows correct portfolio summary
- [ ] Currency conversion is accurate
- [ ] Market prices refresh on app launch
- [ ] Stock-specific fields show only for stock category
- [ ] Form validation works correctly
- [ ] Delete confirmation prevents accidental deletions
- [ ] Error messages are user-friendly
- [ ] Loading states show properly
- [ ] Empty states display correctly
- [ ] App works on different iPhone sizes
- [ ] Dark mode looks good
- [ ] No memory leaks

---

## 8. Future Enhancements (Post-MVP)

### 8.1 Features
- [ ] Multi-device sync (server-side user accounts)
- [ ] Historical price charts for assets
- [ ] Transaction history (buy/sell tracking)
- [ ] Budget tracking
- [ ] Notifications for price alerts
- [ ] Export data (CSV, PDF)
- [ ] Backup/restore
- [ ] Biometric authentication
- [ ] Widget support

### 8.2 Technical
- [ ] Offline mode with local database (Core Data)
- [ ] Background price refresh
- [ ] Push notifications
- [ ] iPad support with adaptive layouts
- [ ] watchOS companion app

---

## 9. Development Best Practices

### 9.1 Code Quality
- Follow Swift API Design Guidelines
- Use SwiftLint for consistent code style
- Write meaningful commit messages
- Keep ViewModels testable (no direct SwiftUI dependencies)
- Separate concerns (View, ViewModel, Service)

### 9.2 Git Workflow
- Work on feature branches
- Use descriptive branch names: `feature/dashboard-view`, `feature/asset-crud`
- Commit frequently with clear messages
- Test before pushing

### 9.3 Documentation
- Add comments for complex logic
- Document API endpoints used
- Keep this RD document updated as development progresses

---

## 10. API Backend Compatibility Notes

### 10.1 Required Backend Endpoints
All endpoints listed in Section 3.2 must be available and working.

### 10.2 Data Format
- Dates: ISO 8601 format (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- Decimal: String representation with up to 2 decimal places
- Currency: 3-letter ISO 4217 code
- UUID: Standard UUID format

### 10.3 Headers
- `X-Device-ID`: Required for market data refresh
- `Content-Type: application/json`: For POST/PUT requests

### 10.4 Query Parameters
- `device_id`: Required for most endpoints
- `base_currency`: Optional, defaults to USD (frontend should send CNY as default)

---

## 11. Quick Reference

### 11.1 Development Cycle Order
1. **Phase 0**: Project Setup & Infrastructure
2. **Phase 1**: Dashboard View (Read-only portfolio display)
3. **Phase 2**: Asset & Credit List Views (Read-only list display)
4. **Phase 3**: Add/Edit Views (Create & Update for BOTH assets and credits)
5. **Phase 4**: Delete Confirmation (Delete for BOTH assets and credits)
6. **Phase 5**: Polish & Testing
7. **Phase 6**: Market Data Integration Testing

### 11.2 Key Decisions Summary
- ✅ CNY as primary currency, all currencies available
- ✅ Implement Assets AND Credits equally
- ✅ Auto-refresh prices on app launch only (no manual button)
- ✅ Native iOS design (don't strictly follow HTML)
- ✅ Device ID: Generate + store in Keychain
- ✅ Develop by pages, but implement Assets AND Credits together when doing Add/Edit/Delete/List

---

## 12. Getting Started Checklist

Before starting development, ensure:
- [ ] Backend is running locally at `http://localhost:8000`
- [ ] All backend endpoints are accessible
- [ ] Test data is available in backend (or can create via API)
- [ ] Xcode 15+ is installed
- [ ] iOS Simulator or physical device ready
- [ ] This RD document is reviewed and understood

---

## 13. Contact & Support

- **Backend API Documentation**: `http://localhost:8000/docs`
- **Backend Repository**: See main project README
- **Questions**: Contact backend developer or project lead

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-01  
**Author**: AI Frontend Master Developer  
**Status**: Ready for Implementation ✅

