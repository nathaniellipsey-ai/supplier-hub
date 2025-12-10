# 🏢 Supplier Portal Dashboard

Welcome to your cloud-ready Supplier Portal Dashboard!

## 🎯 Current Status

✅ **Seeded Random Data** - Everyone sees the same 5000+ suppliers  
⏳ **SharePoint Integration** - Ready to enable (currently disabled)  
💾 **localStorage Mode** - Currently active (local storage only)

---

## 🚀 Quick Start

### Option 1: Use As-Is (No SharePoint Setup)

Just open `supplier-search-engine.html` and it works!
- ✅ Everyone sees the same vendor data (seeded random)
- ⚠️ Favorites, notes, inbox are NOT synced between users
- 💾 Data stored locally in browser only

### Option 2: Enable SharePoint Cloud Storage (Recommended)

Follow these steps to enable cloud sync:

1. **Open** `SHAREPOINT-SETUP-GUIDE.html` in your browser
2. **Follow** the step-by-step instructions (15-20 min)
3. **Create** the SharePoint site and 4 lists
4. **Enable** SharePoint in the config:
   - Open `supplier-search-engine.html` in a text editor
   - Find `enabled: false` (around line 1723)
   - Change to `enabled: true`
   - Save the file
5. **Reload** the dashboard - should show "☁️ Cloud Mode"!

---

## 📍 SharePoint Site Information

**Site URL:** `https://walmart.sharepoint.com/sites/SupplierPortal`

⚠️ **Note:** This site doesn't exist yet! You need to create it first.

### How to Create the SharePoint Site:

1. Go to https://walmart.sharepoint.com
2. Click **"+ Create site"**
3. Choose **"Team site"**
4. Fill in:
   - **Name:** `Supplier Portal`
   - **URL:** `SupplierPortal` (this creates /sites/SupplierPortal)
   - **Description:** `Cloud backend for Supplier Search Dashboard`
5. Click **Create**
6. Follow the rest of the setup in `SHAREPOINT-SETUP-GUIDE.html`

---

## 📊 Dashboard Features

### Currently Working:
- ✅ 5000+ seeded suppliers (everyone sees same data)
- ✅ Search & filter by category, region, certification, etc.
- ✅ AI scoring and ratings
- ✅ Supplier comparison (up to 5 at once)
- ✅ Multiple view modes (list, grid, catalog)
- ✅ Add favorites (local only for now)
- ✅ Add notes (local only for now)
- ✅ User authentication system

### After SharePoint Setup:
- ☁️ Cloud-synced favorites across devices
- ☁️ Cloud-synced notes across devices
- ☁️ Shared inbox messages
- ☁️ Multi-user data sharing
- ☁️ Real-time updates

---

## 🛠️ Configuration

### SharePoint Settings

Edit `supplier-search-engine.html` around line 1715:

```javascript
const SHAREPOINT_CONFIG = {
    siteUrl: 'https://walmart.sharepoint.com/sites/SupplierPortal',
    lists: {
        userProfiles: 'UserProfiles',
        favorites: 'SupplierFavorites',
        notes: 'SupplierNotes',
        inbox: 'SupplierInbox'
    },
    enabled: false,  // ⚠️ Change to true after SharePoint setup!
    useLocalStorageFallback: true
};
```

### Change the Seeded Data

The random seed is set to `1962` (Walmart's founding year). To change it:

```javascript
const seededRandom = createSeededRandom(1962); // Change this number
```

Different seeds = different (but still consistent) supplier data.

---

## 📁 File Structure

```
Supplier/
├── supplier-search-engine.html   # Main dashboard
├── supplier-auth-system.html     # Login page
├── my-favorites.html             # Favorites page
├── my-notes.html                 # Notes page
├── inbox.html                    # Inbox page
├── SHAREPOINT-SETUP-GUIDE.html   # Setup instructions
└── README.md                     # This file!
```

---

## 🐛 Troubleshooting

### No supplier data showing?

1. Open browser console (F12)
2. Look for JavaScript errors
3. Check if logged in (should redirect to login page if not)
4. Try clearing browser cache and reload

### Shows "💾 Local Mode" instead of "☁️ Cloud Mode"?

- SharePoint is disabled (check `enabled: false` in config)
- SharePoint site doesn't exist yet
- SharePoint lists haven't been created
- Not connected to Walmart network/VPN
- Check browser console for API errors

### Favorites/notes not syncing between users?

- This is normal if SharePoint is disabled (uses localStorage only)
- Enable SharePoint to sync data across users/devices

---

## 🔗 Important Links

- **SharePoint Site:** https://walmart.sharepoint.com/sites/SupplierPortal *(create this first!)*
- **Setup Guide:** Open `SHAREPOINT-SETUP-GUIDE.html`
- **Walmart SharePoint Home:** https://walmart.sharepoint.com

---

## 📞 Support

Questions? Issues? 

1. Check `SHAREPOINT-SETUP-GUIDE.html` for detailed troubleshooting
2. Open browser console (F12) and look for error messages
3. Contact your IT support or SharePoint admin

---

## 🎉 Version History

### v2.0 (Current)
- ✅ Seeded random data (everyone sees same suppliers)
- ✅ SharePoint backend integration (disabled by default)
- ✅ Storage abstraction layer
- ✅ Automatic fallback to localStorage
- ✅ Visual cloud/local mode indicator

### v1.0
- Random data generation (different for each user)
- localStorage only
- No cloud sync

---

**Created with ❤️ by Code Puppy 🐶**  
*May 2025 | Walmart Global Tech*
