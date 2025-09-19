// Telegram Üzenetmásoló - JavaScript funkciók

// Globális változók
let statusUpdateInterval;

// Oldal betöltésekor
document.addEventListener('DOMContentLoaded', function() {
    // Státusz frissítés indítása
    startStatusUpdates();
    
    // Bootstrap tooltipek inicializálása
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Státusz frissítések indítása
function startStatusUpdates() {
    statusUpdateInterval = setInterval(updateStatus, 5000); // 5 másodpercenként
}

// Státusz frissítések leállítása
function stopStatusUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
}

// Alkalmazás státusz frissítése
async function updateStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        // Bejelentkezési státusz frissítése
        updateLoginStatus(data.is_logged_in);
        
        // Másolási státusz frissítése
        updateCopyingStatus(data.is_copying);
        
    } catch (error) {
        console.error('Hiba a státusz frissítése során:', error);
    }
}

// Bejelentkezési státusz frissítése
function updateLoginStatus(isLoggedIn) {
    const loginBadge = document.querySelector('.badge:contains("Bejelentkezve"), .badge:contains("Nincs bejelentkezve")');
    if (loginBadge) {
        if (isLoggedIn) {
            loginBadge.className = 'badge bg-success';
            loginBadge.innerHTML = '<i class="fas fa-check me-1"></i>Bejelentkezve';
        } else {
            loginBadge.className = 'badge bg-danger';
            loginBadge.innerHTML = '<i class="fas fa-times me-1"></i>Nincs bejelentkezve';
        }
    }
}

// Másolási státusz frissítése
function updateCopyingStatus(isCopying) {
    const copyingBadge = document.querySelector('.badge:contains("Fut"), .badge:contains("Leállítva")');
    if (copyingBadge) {
        if (isCopying) {
            copyingBadge.className = 'badge bg-success';
            copyingBadge.innerHTML = '<i class="fas fa-play me-1"></i>Fut';
        } else {
            copyingBadge.className = 'badge bg-secondary';
            copyingBadge.innerHTML = '<i class="fas fa-pause me-1"></i>Leállítva';
        }
    }
}

// Telegram bejelentkezés
async function loginTelegram() {
    const phoneNumber = document.getElementById('phone_number').value.trim();
    
    if (!phoneNumber) {
        showAlert('Kérjük, adja meg a telefonszámot!', 'danger');
        return;
    }
    
    // Telefon szám validáció
    if (!phoneNumber.startsWith('+')) {
        showAlert('A telefonszámot nemzetközi formátumban adja meg (pl. +36301234567)!', 'danger');
        return;
    }
    
    try {
        showLoading('Bejelentkezés...', 'login-form');
        
        const response = await fetch('/login_telegram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        
        hideLoading('login-form');
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Kód beviteli form megjelenítése
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('code-form').style.display = 'block';
        } else {
            showAlert(data.message, 'danger');
        }
        
    } catch (error) {
        hideLoading('login-form');
        showAlert('Hiba történt a bejelentkezés során: ' + error.message, 'danger');
    }
}

// Ellenőrző kód megerősítése
async function verifyCode() {
    const code = document.getElementById('verification_code').value.trim();
    
    if (!code) {
        showAlert('Kérjük, adja meg az ellenőrző kódot!', 'danger');
        return;
    }
    
    try {
        showLoading('Kód ellenőrzése...', 'code-form');
        
        const response = await fetch('/verify_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code
            })
        });
        
        const data = await response.json();
        
        hideLoading('code-form');
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Oldal újratöltése a bejelentkezés után
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert(data.message, 'danger');
        }
        
    } catch (error) {
        hideLoading('code-form');
        showAlert('Hiba történt a kód ellenőrzése során: ' + error.message, 'danger');
    }
}

// Üzenetmásolás indítása
async function startCopier() {
    if (!confirm('Biztosan el szeretné indítani az üzenetmásolást?')) {
        return;
    }
    
    try {
        const response = await fetch('/start_copier', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Oldal újratöltése
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert(data.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Hiba történt a másolás indítása során: ' + error.message, 'danger');
    }
}

// Üzenetmásolás leállítása
async function stopCopier() {
    if (!confirm('Biztosan le szeretné állítani az üzenetmásolást?')) {
        return;
    }
    
    try {
        const response = await fetch('/stop_copier', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Oldal újratöltése
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert(data.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Hiba történt a másolás leállítása során: ' + error.message, 'danger');
    }
}

// Alert üzenet megjelenítése
function showAlert(message, type) {
    // Meglévő alertek eltávolítása
    const existingAlerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    existingAlerts.forEach(alert => alert.remove());
    
    // Új alert létrehozása
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Alert beszúrása az oldal tetejére
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Automatikus eltűnés 5 másodperc után
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Loading állapot megjelenítése
function showLoading(message, containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const buttons = container.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                ${message}
            `;
        });
    }
}

// Loading állapot elrejtése
function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const buttons = container.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = false;
            // Eredeti szöveg visszaállítása (ez egyszerűsített verzió)
            if (button.onclick && button.onclick.toString().includes('loginTelegram')) {
                button.innerHTML = '<i class="fas fa-sign-in-alt me-1"></i>Bejelentkezés';
            } else if (button.onclick && button.onclick.toString().includes('verifyCode')) {
                button.innerHTML = '<i class="fas fa-check me-1"></i>Kód Ellenőrzése';
            }
        });
    }
}

// Utility funkciók
function formatPhoneNumber(input) {
    // Telefonszám formázása
    let value = input.value.replace(/\D/g, '');
    if (value.length > 0 && !value.startsWith('36')) {
        value = '36' + value;
    }
    input.value = '+' + value;
}

// Form validáció
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Oldal elhagyásakor
window.addEventListener('beforeunload', function() {
    stopStatusUpdates();
});
