# MoneyInOne — App Store Release Guide

## One-time setup (on your MacBook)

### 1. Install Fastlane
```bash
cd /path/to/MoneyInOne
gem install bundler
bundle install
```

### 2. Create App Store Connect API Key
1. Go to https://appstoreconnect.apple.com → Users & Access → Keys → `+`
2. Name: "Fastlane", Role: **Admin**
3. Download the `.p8` file → save it in the MoneyInOne root as `AuthKey_XXXXXXXXXX.p8`
4. Note the **Key ID** and **Issuer ID**

### 3. Configure credentials
```bash
cp .env.fastlane.example .env.fastlane
# Edit .env.fastlane with your Key ID, Issuer ID, and ITC Team ID
```

### 4. Create the app in App Store Connect (one-time)
1. Go to https://appstoreconnect.apple.com → My Apps → `+` → New App
2. Platform: iOS
3. Bundle ID: `shakewingo.MoneyInOne`
4. SKU: `moneyinone`
5. Save

### 5. Enable GitHub Pages for privacy policy
1. Go to https://github.com/shakewingo/MoneyInOne → Settings → Pages
2. Source: **main branch**, folder: `/docs`
3. Save — privacy policy will be at: https://shakewingo.github.io/MoneyInOne/privacy

---

## Release (every time)

```bash
cd /path/to/MoneyInOne
set -a && source .env.fastlane && set +a
bundle exec fastlane release
```

That's it. Fastlane will:
1. Sync signing certs
2. Build the IPA
3. Upload to App Store Connect
4. Push metadata + screenshots
5. Submit for review

---

## Metadata only (no build)
```bash
bundle exec fastlane metadata_only
```
