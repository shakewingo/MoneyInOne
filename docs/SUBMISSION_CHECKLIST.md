# 📱 MoneyInOne - Quick Submission Checklist

Use this checklist to track your progress toward App Store submission.

---

## Phase 1: Preparation

### App Icon
- [ ] Create 1024x1024 PNG from `ux/app_icon.html`
- [ ] Add to Xcode Assets.xcassets → AppIcon
- [ ] Verify icon appears in app

### Backend Configuration
- [ ] Have production backend URL ready
- [ ] Update production URL in `APIService.swift` (line 26)
- [ ] Verify backend uses HTTPS
- [ ] Test backend connection works
- [ ] Keep development mode ON for now

### Documentation
- [ ] Create privacy policy (use generator if needed)
- [ ] Host privacy policy online (get URL)
- [ ] Create support page or email
- [ ] Prepare app description (see guide)
- [ ] Prepare keywords list

---

## Phase 2: App Metadata

### Text Content
- [ ] App name decided (max 30 chars)
- [ ] Subtitle written (max 30 chars)
- [ ] Full description written (max 4000 chars)
- [ ] Keywords list (max 100 chars)
- [ ] Promotional text (max 170 chars) - optional
- [ ] Version release notes

### Screenshots
- [ ] iPhone 6.7" (1290 x 2796) - 3-10 screenshots
- [ ] iPhone 6.5" (1284 x 2778) - 3-10 screenshots
- [ ] iPad 12.9" (2048 x 2732) - if supporting iPad
- [ ] Screenshots show best features
- [ ] Screenshots are in correct order

### URLs
- [ ] Privacy policy URL (required)
- [ ] Support URL or email (required)
- [ ] Marketing URL (optional)
- [ ] All URLs tested and working

---

## Phase 3: Testing

### Functional Testing
- [ ] Dashboard displays correctly
- [ ] Add asset works
- [ ] Edit asset works
- [ ] Delete asset works
- [ ] Add credit works
- [ ] Edit credit works
- [ ] Delete credit works
- [ ] Multi-currency works
- [ ] Navigation works smoothly
- [ ] No crashes found

### UI Testing
- [ ] Light mode looks good
- [ ] Dark mode looks good
- [ ] All text is readable
- [ ] No UI glitches
- [ ] Animations smooth
- [ ] Empty states look good

### Device Testing
- [ ] Test on iPhone simulator
- [ ] Test on iPad simulator (if supporting)
- [ ] Test on physical device (if available)
- [ ] Portrait orientation works
- [ ] Landscape orientation works (iPhone)

### Edge Cases
- [ ] No internet connection handled
- [ ] Backend errors handled gracefully
- [ ] Empty data states work
- [ ] Large data sets work
- [ ] Long text inputs handled

### Beta Testing (Recommended)
- [ ] Upload TestFlight build
- [ ] Test yourself via TestFlight
- [ ] Invite external testers
- [ ] Collect feedback
- [ ] Fix critical issues

---

## Phase 4: App Store Connect Setup

### Create App Record
- [ ] Log into App Store Connect
- [ ] Create new app
- [ ] Fill in basic information
- [ ] Select bundle ID (shakewingo.MoneyInOne)
- [ ] Set SKU

### App Information
- [ ] Upload screenshots
- [ ] Add description
- [ ] Add keywords
- [ ] Set promotional text
- [ ] Add support URL
- [ ] Add privacy policy URL
- [ ] Add marketing URL (optional)

### Age Rating
- [ ] Complete age rating questionnaire
- [ ] Verify rating is 4+

### App Privacy
- [ ] Fill out privacy questionnaire
- [ ] Declare data collection (financial info, device ID)
- [ ] Specify data usage purposes
- [ ] Publish privacy info

### Pricing
- [ ] Set price (Free recommended)
- [ ] Select availability countries
- [ ] Set availability date

---

## Phase 5: Build and Upload

### Xcode Preparation
- [ ] Open project in Xcode
- [ ] Select "Any iOS Device"
- [ ] Verify signing is working
- [ ] Check version number (1.0)
- [ ] Check build number (1)

### Switch to Production
- [ ] Change `APIConfig.currentEnvironment` to `.production`
- [ ] Verify production URL is correct
- [ ] Build and test once with production mode

### Archive
- [ ] Product → Archive in Xcode
- [ ] Wait for archive to complete
- [ ] Archive appears in Organizer

### Validate
- [ ] Select archive in Organizer
- [ ] Click "Validate App"
- [ ] Choose App Store Connect
- [ ] Validation passes successfully

### Upload
- [ ] Click "Distribute App"
- [ ] Choose App Store Connect → Upload
- [ ] Wait for upload to complete
- [ ] Verify in App Store Connect

### Processing
- [ ] Wait for build processing (10-30 min)
- [ ] Build appears in TestFlight
- [ ] No processing errors

---

## Phase 6: Submit for Review

### Select Build
- [ ] Go to app version in App Store Connect
- [ ] Select the uploaded build
- [ ] Save

### Review Information
- [ ] Add contact information
- [ ] Add notes for reviewers
- [ ] Add demo account (if needed)
- [ ] Choose release option (manual/automatic)

### Final Review
- [ ] All sections show green checkmarks
- [ ] No errors or warnings
- [ ] All information is accurate
- [ ] Screenshots look professional

### Submit
- [ ] Click "Add for Review"
- [ ] Confirm submission
- [ ] Status changes to "Waiting for Review"

---

## Phase 7: After Submission

### Monitoring
- [ ] Check email for updates
- [ ] Check App Store Connect status
- [ ] Monitor review progress

### If Approved
- [ ] Receive approval email
- [ ] Release app (if manual release)
- [ ] Verify app is live
- [ ] Test download from App Store
- [ ] Celebrate! 🎉

### If Rejected
- [ ] Read rejection reason carefully
- [ ] Understand the issue
- [ ] Fix all mentioned problems
- [ ] Increment build number
- [ ] Re-upload and resubmit

---

## Post-Launch

### Monitoring
- [ ] Check crash reports daily
- [ ] Monitor user reviews
- [ ] Respond to user feedback
- [ ] Track download numbers

### Maintenance
- [ ] Plan bug fix updates
- [ ] Plan feature updates
- [ ] Keep backend running smoothly
- [ ] Update app for new iOS versions

---

## Quick Reference

**Current Configuration:**
- Bundle ID: `shakewingo.MoneyInOne`
- Version: 1.0
- Build: 1
- Min iOS: 18.7
- Devices: iPhone & iPad
- Team ID: F53W3K3ZVU

**Important Files:**
- App Icon: `frontend/MoneyInOne/MoneyInOne/Assets.xcassets/AppIcon.appiconset/`
- API Config: `frontend/MoneyInOne/MoneyInOne/Services/APIService.swift`
- Info.plist: `frontend/MoneyInOne/MoneyInOne/Info.plist`

**Key Settings to Change Before Submission:**
1. Add app icon (1024x1024 PNG)
2. Update production URL in APIService.swift (line 26)
3. Switch to production mode (line 37)
4. Test thoroughly!

---

## Estimated Timeline

- **Preparation**: 1-2 days
- **Testing**: 2-3 days
- **App Store Connect Setup**: 1-2 hours
- **Build & Upload**: 1 hour
- **Apple Review**: 1-3 days
- **Total**: ~1 week from start to approval

---

## Need Help?

See the detailed `APP_STORE_SUBMISSION_GUIDE.md` for step-by-step instructions on each item.

**Good luck! 🚀**

