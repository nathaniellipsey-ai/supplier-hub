# Frontend Integration Guide

## How to Connect the New Features to Your Dashboard

Your dashboard already has the UI for favorites, notes, and inbox. Now we'll hook them up to the backend!

---

## Step 1: Add Auth Script to Dashboard

The dashboard's `index.html` needs to load the auth client. Add this before closing `</body>`:

```html
<!-- Authentication Client -->
<script src="js/auth-client.js"></script>
```

That's it! The `authClient` object is now available globally.

---

## Step 2: Add Login Modal

Add this HTML to your dashboard to create a login modal:

```html
<div id="loginModal" class="modal" style="display: none;">
  <div class="modal-content" style="max-width: 400px; padding: 30px;">
    <h2>Login to Supplier Hub</h2>
    <p style="margin-bottom: 20px; font-size: 14px; color: #666;">
      Please login to save favorites and notes
    </p>
    
    <div style="margin-bottom: 15px;">
      <input type="email" id="loginEmail" placeholder="Email" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
    </div>
    
    <div style="margin-bottom: 15px;">
      <input type="text" id="loginName" placeholder="Name" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
    </div>
    
    <div style="margin-bottom: 20px;">
      <input type="text" id="loginWalmartId" placeholder="Walmart ID (optional)" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
    </div>
    
    <div style="display: flex; gap: 10px;">
      <button id="loginSSOBtn" class="btn" style="flex: 1; background: #0071ce; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
        Login with Walmart
      </button>
      <button id="loginGuestBtn" class="btn" style="flex: 1; background: #666; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
        Login as Guest
      </button>
    </div>
  </div>
</div>
```

---

## Step 3: Add CSS

Add this CSS to your `frontend/css/style.css`:

```css
.modal {
  display: none;
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: white;
  margin: auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 90%;
}
```

---

## Step 4: Add Login Script

Add this JavaScript to initialize login:

```javascript
function initializeLogin() {
  const loginModal = document.getElementById('loginModal');
  const loginSSOBtn = document.getElementById('loginSSOBtn');
  const loginGuestBtn = document.getElementById('loginGuestBtn');
  
  if (!authClient.isAuthenticated) {
    loginModal.style.display = 'block';
  }
  
  loginSSOBtn.addEventListener('click', async () => {
    const email = document.getElementById('loginEmail').value;
    const name = document.getElementById('loginName').value;
    const walmartId = document.getElementById('loginWalmartId').value;
    
    if (!email || !name) {
      alert('Please fill in email and name');
      return;
    }
    
    try {
      await authClient.loginWithSSO(walmartId || 'GUEST', email, name);
      loginModal.style.display = 'none';
      showNotification('Welcome! You are now logged in.');
      loadInbox();
    } catch (error) {
      alert('Login failed: ' + error.message);
    }
  });
  
  loginGuestBtn.addEventListener('click', async () => {
    const email = document.getElementById('loginEmail').value;
    const name = document.getElementById('loginName').value;
    
    if (!email || !name) {
      alert('Please fill in email and name');
      return;
    }
    
    try {
      await authClient.loginAsGuest(email, name);
      loginModal.style.display = 'none';
      showNotification('Welcome! You are now logged in as a guest.');
      loadInbox();
    } catch (error) {
      alert('Login failed: ' + error.message);
    }
  });
  
  window.addEventListener('auth-changed', (e) => {
    if (e.detail.authenticated) {
      loginModal.style.display = 'none';
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeLogin);
} else {
  initializeLogin();
}
```

---

## Step 5: Connect Favorites

Replace your `toggleFavorite` function:

```javascript
async function toggleFavorite(supplierId, supplierName = 'Unknown') {
  if (!authClient.isAuthenticated) {
    showNotification('Please login to save favorites');
    document.getElementById('loginModal').style.display = 'block';
    return;
  }
  
  try {
    const isFav = await authClient.isFavorite(supplierId);
    
    if (isFav) {
      await authClient.removeFavorite(supplierId);
      showNotification('Removed from favorites');
    } else {
      await authClient.addFavorite(supplierId, supplierName);
      showNotification('Added to favorites!');
    }
    
    updateFavoriteButtons();
  } catch (error) {
    showNotification('Error: ' + error.message);
  }
}
```

---

## Step 6: Connect Notes

Update your note functions:

```javascript
async function openNoteModal(supplierId) {
  if (!authClient.isAuthenticated) {
    showNotification('Please login to add notes');
    document.getElementById('loginModal').style.display = 'block';
    return;
  }
  
  const modal = document.getElementById('noteModal');
  if (modal) {
    modal.style.display = 'block';
    modal.dataset.supplierId = supplierId;
    
    const notes = await authClient.getNotes(supplierId);
    const notesContainer = document.getElementById('notesContainer');
    if (notesContainer && notes.count > 0) {
      notesContainer.innerHTML = notes.notes.map(note => `
        <div style="padding: 10px; background: #f9f9f9; border-radius: 4px; margin-bottom: 10px;">
          <p>${note.content}</p>
          <small style="color: #999;">${new Date(note.created_at).toLocaleDateString()}</small>
          <button onclick="deleteNote('${note.id}')">Delete</button>
        </div>
      `).join('');
    }
  }
}

async function saveNote(supplierId, content) {
  if (!authClient.isAuthenticated) return;
  
  try {
    await authClient.addNote(supplierId, content);
    showNotification('Note saved!');
  } catch (error) {
    showNotification('Error: ' + error.message);
  }
}

async function deleteNote(noteId) {
  try {
    await authClient.deleteNote(noteId);
    showNotification('Note deleted');
  } catch (error) {
    showNotification('Error: ' + error.message);
  }
}
```

---

## Step 7: Connect Inbox

Add this function:

```javascript
async function loadInbox() {
  if (!authClient.isAuthenticated) return;
  
  try {
    const inbox = await authClient.getInbox();
    const badge = document.getElementById('inboxBadge');
    
    if (badge && inbox.unread_count > 0) {
      badge.textContent = inbox.unread_count;
      badge.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading inbox:', error);
  }
}

setInterval(() => {
  if (authClient.isAuthenticated) loadInbox();
}, 30000);
```

---

## Step 8: Test Everything

1. Start backend: `START_BACKEND.bat`
2. Start frontend: `START_FRONTEND.bat`
3. Login with email and name
4. Try adding a favorite
5. Try adding a note
6. Check inbox

Everything should work!

---

## Summary

You now have a complete user system with:
- Authentication (SSO + Guest)
- Favorites management
- Notes system  
- Inbox/messages
- Session persistence

Happy coding!
