# Phase 3: Add/Edit Views Development 📝

**Status:** ✅ EXECUTION COMPLETE  
**Mode:** Executor  
**Last Updated:** October 2, 2025

---

## Background and Motivation

### Project Context
MoneyInOne Phase 2 successfully delivered functional Assets and Credits List Views with swipe actions, delete confirmation, and state management. Phase 3 focuses on building **unified Add/Edit form views** that allow users to create new financial records and edit existing ones.

### Phase 3 Goals
Build fully functional Add/Edit views for both Assets and Credits that:
1. Work for both Add and Edit modes in a single unified component
2. Support both Assets and Credits with appropriate field differences
3. Show/hide stock-specific fields (symbol, shares) dynamically
4. Validate user input before submission
5. Handle create and update API operations
6. Navigate back to list view on success
7. Show delete button in Edit mode only
8. Provide excellent UX with loading states and error handling

### UX Design Reference
Based on `ux/add_form.html` and `ux/edit_form.html`, the form should include:
- **Form Fields**:
  - Category picker (Asset or Credit categories)
  - Name text field
  - Currency picker (CNY default)
  - Amount field with currency symbol
  - Date picker (purchase_date or issue_date)
  - Notes textarea (optional)
  - **Stock-specific** (shown only for stock/crypto): Symbol, Shares
- **Action Buttons**:
  - Cancel button (dismisses form)
  - Save button (Add Asset/Credit or Update Asset/Credit)
  - Delete button (only in Edit mode, at bottom)

---

## Key Challenges and Analysis

### Technical Challenges

#### 1. **Unified Form for Multiple Modes**
- **Challenge**: Single form component needs to handle 4 modes: Add Asset, Edit Asset, Add Credit, Edit Credit
- **Solution**: Use enum `FormMode { addAsset, editAsset(Asset), addCredit, editCredit(Credit) }`
- **Rationale**: DRY principle, single source of truth for form UI

#### 2. **Dynamic Form Fields**
- **Challenge**: Stock/crypto categories require additional fields (symbol, shares)
- **Solution**: Conditional rendering based on selected category
- **Rationale**: Better UX than showing disabled fields

#### 3. **Form Validation**
- **Challenge**: Different validation rules for different modes and categories
- **Solution**: Centralized validation in ViewModel with clear error messages
- **Rationale**: Reusable, testable, user-friendly

#### 4. **Navigation and Data Flow**
- **Challenge**: Navigate from List → Add/Edit, pass data, refresh list on return
- **Solution**: Use SwiftUI NavigationStack with @State for presentation
- **Rationale**: Modern SwiftUI navigation, proper data flow

#### 5. **Date Handling**
- **Challenge**: Assets use `purchase_date`, Credits use `issue_date`
- **Solution**: Single DatePicker, label changes based on mode
- **Rationale**: Consistent UI, simple implementation

#### 6. **Decimal Input**
- **Challenge**: Amount and shares need different input types (currency vs integer/decimal)
- **Solution**: Custom TextField with proper keyboard types and formatting
- **Rationale**: Native iOS behavior, better UX

---

## High-Level Task Breakdown

### Task 1: Create FormMode Enum
**File**: `Models/FormMode.swift` (new)  
**Dependencies**: Asset, Credit models  
**Estimated Effort**: 15 minutes

**Description**: Create an enum to represent all form modes with associated data.

**Requirements**:
- Define enum with 4 cases
- Associated values for edit modes
- Helper computed properties

**Success Criteria**:
- [ ] Enum supports all 4 modes
- [ ] Edit modes carry the item being edited
- [ ] Computed properties for isEditMode, isAssetMode, etc.

**Implementation Notes**:
```swift
enum FormMode: Identifiable {
    case addAsset
    case editAsset(Asset)
    case addCredit
    case editCredit(Credit)
    
    var id: String {
        switch self {
        case .addAsset: return "addAsset"
        case .editAsset(let asset): return "editAsset-\(asset.id)"
        case .addCredit: return "addCredit"
        case .editCredit(let credit): return "editCredit-\(credit.id)"
        }
    }
    
    var isEditMode: Bool {
        switch self {
        case .editAsset, .editCredit: return true
        default: return false
        }
    }
    
    var isAssetMode: Bool {
        switch self {
        case .addAsset, .editAsset: return true
        default: return false
        }
    }
    
    var title: String {
        switch self {
        case .addAsset: return "Add Asset"
        case .editAsset: return "Edit Asset"
        case .addCredit: return "Add Credit"
        case .editCredit: return "Edit Credit"
        }
    }
}
```

---

### Task 2: Create AddEditViewModel
**File**: `ViewModels/AddEditViewModel.swift` (new)  
**Dependencies**: AssetService, CreditService, FormMode  
**Estimated Effort**: 90 minutes

**Description**: Implement observable view model to manage form state, validation, and submission.

**Requirements**:
- Use `@Observable` macro for reactive updates
- Manage form fields (name, category, amount, currency, date, notes, symbol, shares)
- Validate input based on mode and category
- Submit to appropriate API endpoint
- Handle loading and error states
- Clear validation on field change

**Success Criteria**:
- [ ] ViewModel initializes with form mode
- [ ] Form fields pre-populated in edit mode
- [ ] Validation works for all required fields
- [ ] Stock/crypto validation includes symbol and shares
- [ ] Submit creates or updates based on mode
- [ ] Loading indicator shown during submission
- [ ] Error messages displayed clearly
- [ ] Success triggers navigation back

**Implementation Notes**:
- Properties:
  - `mode: FormMode`
  - `name: String`
  - `selectedCategory: AssetCategory or CreditCategory`
  - `amount: String` (use String for TextField binding)
  - `currency: Currency`
  - `date: Date`
  - `notes: String`
  - `symbol: String`
  - `shares: String`
  - `isLoading: Bool`
  - `errorMessage: String?`
  - `validationErrors: [String: String]` (field-specific errors)
- Methods:
  - `validateForm() -> Bool`
  - `submitForm(deviceId:) async throws`
  - `deleteItem(deviceId:) async throws`
  - Helper: `requiresStockFields: Bool` computed property

---

### Task 3: Build CategoryPicker Component
**File**: `Views/Common/CategoryPicker.swift` (new)  
**Dependencies**: AssetCategory, CreditCategory  
**Estimated Effort**: 25 minutes

**Description**: Create reusable picker for selecting asset or credit category.

**Requirements**:
- Support both asset and credit categories
- Display category icons and names
- Use native iOS Picker style
- Show selected category with icon

**Success Criteria**:
- [ ] Picker shows all categories for given type
- [ ] Each item shows icon and display name
- [ ] Selection updates binding correctly
- [ ] Works for both assets and credits

**Implementation Notes**:
```swift
struct CategoryPicker<Category: CaseIterable & RawRepresentable & Identifiable>: View 
    where Category.RawValue == String {
    @Binding var selection: Category
    let categories: [Category]
    
    var body: some View {
        Picker("Category", selection: $selection) {
            ForEach(categories) { category in
                Label(category.displayName, systemImage: category.iconName)
                    .tag(category)
            }
        }
        .pickerStyle(.menu)
    }
}
```

---

### Task 4: Build CurrencyPickerView Component
**File**: `Views/Common/CurrencyPickerView.swift` (new)  
**Dependencies**: Currency enum  
**Estimated Effort**: 20 minutes

**Description**: Create picker for selecting currency in forms.

**Requirements**:
- List all available currencies
- Show currency code and name (e.g., "USD - US Dollar")
- CNY as default
- Inline picker style for forms

**Success Criteria**:
- [ ] Picker shows all currencies
- [ ] Display format: "CODE - Name"
- [ ] Selection updates binding
- [ ] Default to CNY for new items

**Implementation Notes**:
- Use `Picker` with `.menu` style
- Each currency shows both code and full name
- Reusable across add/edit forms

---

### Task 5: Build AmountTextField Component
**File**: `Views/Common/AmountTextField.swift` (new)  
**Dependencies**: None  
**Estimated Effort**: 30 minutes

**Description**: Create custom text field for currency amount input with formatting.

**Requirements**:
- Accept decimal input
- Show currency symbol prefix
- Validate numeric input
- Proper keyboard type (decimal pad)
- Format on entry

**Success Criteria**:
- [ ] Only accepts numeric input
- [ ] Currency symbol shown as prefix
- [ ] Keyboard shows decimal pad
- [ ] Formats to 2 decimal places on blur
- [ ] Binding updates correctly

**Implementation Notes**:
```swift
struct AmountTextField: View {
    @Binding var amount: String
    let currencySymbol: String
    let placeholder: String
    
    var body: some View {
        HStack {
            Text(currencySymbol)
                .foregroundColor(.secondary)
            TextField(placeholder, text: $amount)
                .keyboardType(.decimalPad)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}
```

---

### Task 6: Build AddEditFormView
**File**: `Views/AddEdit/AddEditFormView.swift` (new)  
**Dependencies**: AddEditViewModel, all form components  
**Estimated Effort**: 120 minutes

**Description**: Create main form view that works for all modes (Add/Edit Asset/Credit).

**Requirements**:
- NavigationStack with title based on mode
- All form fields in scrollable form
- Conditional stock-specific fields
- Cancel and Save buttons in toolbar
- Delete button at bottom (edit mode only)
- Loading overlay during submission
- Error display
- Keyboard dismissal

**Success Criteria**:
- [ ] Form displays correctly for all modes
- [ ] Fields pre-populated in edit mode
- [ ] Stock/crypto fields show/hide based on category
- [ ] Validation errors shown inline
- [ ] Save button triggers submission
- [ ] Cancel button dismisses form
- [ ] Delete button shown only in edit mode
- [ ] Loading indicator during save/delete
- [ ] Navigation back on success
- [ ] Error alerts displayed

**Implementation Notes**:
- Use `Form` with sections
- Sections:
  1. Category picker
  2. Basic info (name, currency, amount, date)
  3. Stock-specific (conditional)
  4. Notes (optional)
  5. Actions (Save, Delete)
- Toolbar: Cancel button (leading), Save button (trailing)
- Delete button: Bottom of form, destructive style
- Use `.disabled()` modifier on save button while loading
- Show progress view overlay during submission

---

### Task 7: Add Navigation to List Views
**File**: Update `AssetListView.swift` and `CreditListView.swift`  
**Dependencies**: AddEditFormView  
**Estimated Effort**: 40 minutes

**Description**: Wire up navigation from list views to add/edit forms.

**Requirements**:
- "+" button opens add form as sheet
- Tap on row opens edit form as sheet
- Pass correct FormMode to form
- Refresh list when sheet dismisses

**Success Criteria**:
- [ ] "+ Asset" button opens add asset form
- [ ] "+ Credit" button opens add credit form
- [ ] Tapping asset row opens edit asset form
- [ ] Tapping credit row opens edit credit form
- [ ] Form presented as sheet
- [ ] List refreshes after form dismisses
- [ ] Navigation feels natural

**Implementation Notes**:
```swift
@State private var presentedFormMode: FormMode?

// In toolbar
.toolbar {
    ToolbarItem(placement: .trailing) {
        Button {
            presentedFormMode = .addAsset
        } label: {
            Image(systemName: "plus")
        }
    }
}

// Sheet presentation
.sheet(item: $presentedFormMode) { mode in
    NavigationStack {
        AddEditFormView(mode: mode)
    }
}
```

---

### Task 8: Implement Delete in Edit Form
**File**: Update `AddEditViewModel.swift` and `AddEditFormView.swift`  
**Dependencies**: AssetService, CreditService  
**Estimated Effort**: 30 minutes

**Description**: Add delete functionality to edit forms with confirmation.

**Requirements**:
- Delete button only visible in edit mode
- Confirmation alert before deletion
- Call appropriate delete API
- Navigate back on success
- Show error if deletion fails

**Success Criteria**:
- [ ] Delete button appears only in edit mode
- [ ] Alert shows item name and warning
- [ ] Confirmation required before deletion
- [ ] API called correctly
- [ ] Form dismisses on successful deletion
- [ ] Error shown if deletion fails

**Implementation Notes**:
- Delete button styling: `.buttonStyle(.borderedProminent).tint(.red)`
- Confirmation alert: Show item name, "This action cannot be undone"
- After successful deletion, use `@Environment(\.dismiss)` to close form

---

### Task 9: Add Form Validation
**File**: `AddEditViewModel.swift`  
**Dependencies**: None  
**Estimated Effort**: 40 minutes

**Description**: Implement comprehensive form validation with user-friendly error messages.

**Requirements**:
- Name: Required, non-empty
- Amount: Required, > 0, valid decimal
- Category: Required
- Date: Required
- Symbol: Required if stock/crypto
- Shares: Required if stock/crypto, > 0

**Success Criteria**:
- [ ] All required fields validated
- [ ] Validation happens on submit
- [ ] Clear error messages
- [ ] Field-specific error display
- [ ] Stock-specific validation works
- [ ] Form cannot submit with errors

**Implementation Notes**:
```swift
func validateForm() -> Bool {
    validationErrors.removeAll()
    
    if name.trimmingCharacters(in: .whitespaces).isEmpty {
        validationErrors["name"] = "Name is required"
    }
    
    guard let amountValue = Decimal(string: amount), amountValue > 0 else {
        validationErrors["amount"] = "Amount must be greater than 0"
        return false
    }
    
    // Stock-specific validation
    if requiresStockFields {
        if symbol.trimmingCharacters(in: .whitespaces).isEmpty {
            validationErrors["symbol"] = "Symbol is required for stocks/crypto"
        }
        // ... shares validation
    }
    
    return validationErrors.isEmpty
}
```

---

### Task 10: Test All Form Scenarios
**File**: Manual testing  
**Dependencies**: All above components  
**Estimated Effort**: 45 minutes

**Description**: Comprehensively test all form scenarios and edge cases.

**Test Cases**:
1. **Add Asset**:
   - Fill all fields, submit successfully
   - Try to submit with empty name → error
   - Try to submit with zero amount → error
   - Change category to stock → symbol/shares appear
   - Cancel form → dismisses without saving
   
2. **Edit Asset**:
   - Fields pre-populated correctly
   - Modify values, save successfully
   - Delete button appears
   - Delete with confirmation works
   
3. **Add Credit**:
   - Similar to Add Asset
   - No stock-specific fields
   
4. **Edit Credit**:
   - Similar to Edit Asset
   - No stock-specific fields
   
5. **Stock/Crypto Specific**:
   - Add stock with symbol and shares
   - Edit stock, modify symbol/shares
   - Validation requires symbol and shares
   
6. **Edge Cases**:
   - Network error during save
   - Network error during delete
   - Invalid amount format
   - Very large numbers
   - Special characters in name

**Success Criteria**:
- [ ] All add operations work
- [ ] All edit operations work
- [ ] All delete operations work
- [ ] All validations work correctly
- [ ] Error handling works
- [ ] UI remains responsive
- [ ] No crashes

---

## Project Status Board

### Task Status Overview
- [x] Task 1: FormMode Enum - ✅ COMPLETED
- [x] Task 2: AddEditViewModel - ✅ COMPLETED
- [x] Task 3: CategoryPicker Component - ✅ COMPLETED (used Picker directly)
- [x] Task 4: CurrencyPickerView Component - ✅ COMPLETED
- [x] Task 5: AmountTextField Component - ✅ COMPLETED
- [x] Task 6: AddEditFormView - ✅ COMPLETED
- [x] Task 7: Navigation to List Views - ✅ COMPLETED
- [x] Task 8: Delete in Edit Form - ✅ COMPLETED
- [x] Task 9: Form Validation - ✅ COMPLETED
- [ ] Task 10: Test All Scenarios - READY FOR USER TESTING

### Dependencies Graph
```
Task 1 (FormMode) → Task 2 (ViewModel) → Task 6 (FormView)
                                            ↓
Task 3 (CategoryPicker) ------------------→ Task 6
Task 4 (CurrencyPicker) ------------------→ Task 6
Task 5 (AmountTextField) ------------------→ Task 6
                                            ↓
Task 2 (ViewModel) → Task 9 (Validation) → Task 6
Task 2 (ViewModel) → Task 8 (Delete) ----→ Task 6
                                            ↓
Task 6 (FormView) → Task 7 (Navigation) → Task 10 (Testing)
```

**Recommended Execution Order**:
1. Task 1 (FormMode) - Foundation enum
2. Tasks 3, 4, 5 (Form components) - Can be done in parallel
3. Task 2 (ViewModel) - Depends on Task 1
4. Task 9 (Validation) - Extends Task 2
5. Task 6 (FormView) - Depends on all above
6. Task 8 (Delete) - Extends Task 6
7. Task 7 (Navigation) - Integrates with list views
8. Task 10 (Testing) - Final validation

---

## API Endpoints Reference

### Assets
- `POST /api/v1/assets` (Header: X-Device-ID) - Create asset
  ```json
  {
    "name": "string",
    "category": "stock",
    "amount": "1000.00",
    "currency": "USD",
    "purchase_date": "2024-01-15T00:00:00Z",
    "notes": "string",
    "symbol": "AAPL",
    "shares": 10.0,
    "is_market_tracked": true
  }
  ```

- `PUT /api/v1/assets/{id}?device_id={id}` - Update asset
  ```json
  {
    "name": "string",
    "amount": "1200.00",
    // ... partial update
  }
  ```

### Credits
- `POST /api/v1/credits` (Header: X-Device-ID) - Create credit
  ```json
  {
    "name": "string",
    "category": "credit_card",
    "amount": "5000.00",
    "currency": "USD",
    "issue_date": "2024-01-15T00:00:00Z",
    "notes": "string"
  }
  ```

- `PUT /api/v1/credits/{id}?device_id={id}` - Update credit
  ```json
  {
    "name": "string",
    "amount": "4500.00",
    // ... partial update
  }
  ```

---

## Design Guidelines for This Phase

### Form UX Principles
1. **Clear Labels**: Every field has a descriptive label
2. **Validation Feedback**: Show errors inline near the field
3. **Smart Defaults**: CNY currency, today's date
4. **Progressive Disclosure**: Show stock fields only when needed
5. **Keyboard Optimization**: Appropriate keyboard for each field type
6. **Error Prevention**: Disable save button during loading
7. **Confirmation**: Always confirm destructive actions

### Layout Guidelines
- **Form Sections**: Group related fields
- **Field Spacing**: 16pt between fields, 24pt between sections
- **Button Placement**: Cancel (leading), Save (trailing), Delete (bottom)
- **Input Height**: 44pt minimum for touch targets
- **Padding**: 16pt horizontal padding in forms

### Color Scheme
- **Primary Action**: Blue (Save button)
- **Destructive Action**: Red (Delete button)
- **Cancel**: Gray (secondary)
- **Error Text**: Red with warning icon
- **Validation**: Red border on invalid fields

---

## Success Criteria for Phase 3

### Functional Requirements
- ✅ Can create new assets with all fields
- ✅ Can create new credits with all fields
- ✅ Can edit existing assets
- ✅ Can edit existing credits
- ✅ Stock-specific fields show/hide correctly
- ✅ Form validation prevents invalid submissions
- ✅ Delete from edit form works
- ✅ List refreshes after add/edit/delete

### UX Requirements
- ✅ Form feels responsive and native
- ✅ Loading states prevent double-submission
- ✅ Error messages are clear and helpful
- ✅ Keyboard dismisses when appropriate
- ✅ Navigation feels natural
- ✅ No UI glitches or crashes

### Technical Requirements
- ✅ API integration works correctly
- ✅ State management is clean
- ✅ No memory leaks
- ✅ Code is maintainable and well-documented

---

## Executor Notes

### Before Starting Execution
- [ ] Review frontend_rd.md Phase 3 requirements
- [ ] Check UX design in add_form.html and edit_form.html
- [ ] Ensure Phase 2 list views are working
- [ ] Backend endpoints tested and working

### During Execution
- Build components bottom-up (enum → components → viewmodel → view)
- Test each component individually before integration
- Use SwiftUI Previews for rapid iteration
- Keep validation logic centralized in ViewModel

### After Completion
- Run comprehensive testing (Task 10)
- Verify no regressions in list views
- Test on different device sizes
- Check accessibility

---

## Executor Feedback or Help Requests

### ✅ Phase 3 Execution Summary

**Completed:** October 2, 2025  
**Total Time:** ~2.5 hours (actual execution)  
**Status:** ALL TASKS COMPLETE (1-9) ✅

#### Files Created:

**Models (New):**
- ✅ `Models/FormMode.swift` - Enum for Add/Edit modes with computed properties

**ViewModels (New):**
- ✅ `ViewModels/AddEditViewModel.swift` - Form state management with validation

**UI Components (New):**
- ✅ `Views/Common/AmountTextField.swift` - Custom currency input field
- ✅ `Views/Common/CurrencyPickerView.swift` - Currency selection picker
- ✅ `Views/AddEdit/AddEditFormView.swift` - Unified form for all modes

**Modified:**
- ✅ `Models/Currency.swift` - Added `displayName` property
- ✅ `Views/Assets/AssetListView.swift` - Added form navigation and refresh
- ✅ `Views/Credits/CreditListView.swift` - Added form navigation and refresh

#### Key Features Implemented:

1. **Unified Form Design** ✅
   - Single form component handles 4 modes
   - Add Asset, Edit Asset, Add Credit, Edit Credit
   - Mode determined by FormMode enum

2. **Dynamic Field Visibility** ✅
   - Stock-specific fields (symbol, shares) show only for stock/crypto
   - Automatically hides when switching to other categories
   - Clean, progressive disclosure UX

3. **Comprehensive Validation** ✅
   - Name: Required, non-empty
   - Amount: Required, > 0, valid decimal
   - Symbol: Required for stock/crypto
   - Shares: Required for stock/crypto, > 0
   - Field-specific error messages displayed inline

4. **Full CRUD Integration** ✅
   - Create new assets and credits
   - Update existing assets and credits
   - Delete from edit form with confirmation
   - Proper API integration with error handling

5. **Navigation Flow** ✅
   - "+" button → Add form (sheet presentation)
   - Tap row → Edit form (sheet presentation)
   - Swipe right → Edit form
   - Empty state CTA → Add form
   - List auto-refreshes after form dismissal

6. **Loading States** ✅
   - Loading overlay during submission
   - Disabled save button while loading
   - Error display with retry capability

7. **Delete Confirmation** ✅
   - Delete button only in edit mode
   - Alert shows item name
   - Clear warning message
   - Confirmation required before deletion

#### Architecture Highlights:

- **Type-Safe Form Modes**: FormMode enum with associated values
- **Reactive State**: @Observable macro for ViewModel
- **Sheet Presentation**: Modern SwiftUI navigation
- **Form Validation**: Centralized in ViewModel
- **Error Handling**: User-friendly messages
- **Auto-Refresh**: List updates after form actions
- **Currency Support**: Default CNY, full picker
- **Date Handling**: Proper labels (Purchase Date vs Issue Date)

#### No Linter Errors ✅

All 8 files compiled successfully with zero linter errors.

#### Ready for Testing (Task 10):

The app is ready for comprehensive testing. User should test:

**Add Asset Scenarios:**
1. Add cash asset → Success
2. Add stock with symbol/shares → Success
3. Try to submit without name → Validation error
4. Try to submit with zero amount → Validation error
5. Add stock without symbol → Validation error
6. Change category from stock to cash → Symbol/shares hide

**Edit Asset Scenarios:**
7. Edit existing asset → Fields pre-populated
8. Modify name and amount → Update succeeds
9. Delete asset from edit form → Confirmation shown
10. Cancel edit → No changes saved

**Add Credit Scenarios:**
11. Add credit card → Success
12. Add mortgage → Success
13. Validation works same as assets

**Edit Credit Scenarios:**
14. Edit existing credit → Works correctly
15. Delete credit → Works correctly

**Stock-Specific:**
16. Add AAPL with 100 shares → Success
17. Edit stock, change symbol → Update works
18. Add crypto (BTC) with 0.5 coins → Success

**Edge Cases:**
19. Network error during save → Error shown
20. Network error during delete → Error shown
21. Very large amounts → Handles correctly
22. Special characters in name → Handles correctly

**UI/UX:**
23. Form presented as sheet
24. List refreshes after adding item
25. List refreshes after editing item
26. List refreshes after deleting item
27. Currency picker works in form
28. Date picker works correctly
29. Keyboard dismisses properly
30. Loading overlay blocks interaction

#### Next Phase:

Phase 3 complete! Ready for final polish and testing.

---

# Previous Phases Summary

## Phase 1: Dashboard View ✅ COMPLETE
- Portfolio summary card
- Asset breakdown chart
- Top assets list
- Market price refresh
- Currency switching

## Phase 2: Assets & Credits List Views ✅ COMPLETE
- Grouped category display
- Swipe actions (delete only - tap for edit)
- Delete confirmation
- Pull-to-refresh
- Loading/error/empty states
- Currency support

---

# Technical Debt
(Preserved from Phase 2 - no changes)

## 👤 Multi-Device Sync (User Authentication)

### Current Architecture Problem:
- Using `device_id` → data tied to device
- Different devices = different data

### Recommended Solution: Add User Authentication

You have **3 options**:

### **Option A: Username/Password (Traditional)**

```
Flow:
1. User creates account (username/password)
2. Backend creates user_id, links to device
3. User logs in on Device B
4. Device B now sees same data
```

**Backend changes needed:**
```python
# Add authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

# Endpoints accept JWT token instead of device_id
@router.get("/portfolio/summary")
async def get_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    base_currency: str = "USD"
):
    user_id = verify_token(credentials.credentials)  # Get user from JWT
    # ... rest of logic
```

**Frontend changes needed:**
```swift
// Add login screen
// Store JWT token in Keychain
// Send token in API requests
```

### **Option B: Device Linking (Simpler)**

Allow users to link devices without full authentication:

```
Flow:
1. Device A generates account_code (e.g., "ABC-123")
2. User enters code on Device B
3. Backend links Device B to same user_id
4. Both devices share data
```

**Backend changes:**
```python
class User:
    id: UUID
    devices: List[str]  # Multiple device IDs
    
@router.post("/devices/link")
async def link_device(code: str, device_id: str):
    # Find user by code, add device_id to devices list
```

### **Option C: Email/Magic Link (Modern, Passwordless)**

```
Flow:
1. User enters email
2. Backend sends magic link
3. User clicks link → device authenticated
4. Same on Device B
```

## Market price calculation issue when switching to currency

## ~~Stylish UI~~