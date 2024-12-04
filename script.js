// Check if a string contains sequential characters 
function containsSequential(password) { 
    let lowerPassword = password.toLowerCase(); 
    for (let i = 0; i < lowerPassword.length - 2; i++) { 
        let first = lowerPassword.charCodeAt(i); 
        let second = lowerPassword.charCodeAt(i + 1); 
        let third = lowerPassword.charCodeAt(i + 2); 
        if ((second === first + 1) && (third === second + 1)) { 
            return true; 
        } 
    } 
    return false; 
} 
 
// Check password strength 
function isStrongPassword(password) { 
    if (password.length < 10) return { strong: false, level: 1 }; 
 
    let hasUpperCase = /[A-Z]/.test(password); 
    let hasLowerCase = /[a-z]/.test(password); 
    let hasDigit = /[0-9]/.test(password); 
    let hasSpecialChar = /[_.*@]/.test(password); 
 
    if (!hasUpperCase || !hasLowerCase  || !hasDigit || !hasSpecialChar) { 
        return { strong: false, level: 2 }; 
    } 
 
    if (containsSequential(password)) { 
        return { strong: false, level: 3 }; 
    } 
 
    return { strong: true, level: 4 }; 
} 
 
// Update UI with password strength 
function checkPassword() { 
    const passwordInput = document.getElementById("passwordInput").value; 
    const result = document.getElementById("result"); 
    const strengthBar = document.getElementById("strengthBar"); 
 
    const { strong, level } = isStrongPassword(passwordInput); 
 
    let strengthWidth = level * 25; // Map level to percentage (0-100) 
    strengthBar.style.width = strengthWidth + "%"; 
 
    if (level === 1) { 
        strengthBar.style.background = "#ff4b1f"; // Red 
        result.textContent = "Very Weak"; 
    } else if (level === 2) { 
        strengthBar.style.background = "#ff9068"; // Orange 
        result.textContent = "Weak"; 
    } else if (level === 3) { 
        strengthBar.style.background = "#ffc300"; // Yellow 
        result.textContent = "Moderate"; 
    } else if (level === 4) { 
        strengthBar.style.background = "#4caf50"; // Green 
        result.textContent = strong ? "Strong Password!" : "Weak Password"; 
    } 
}