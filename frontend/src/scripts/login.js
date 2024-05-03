 document.addEventListener('DOMContentLoaded', function () {
            const API_BASE_URL = 'http://127.0.0.1:5000';
            const loginButton = document.querySelector('#loginButton');

            loginButton.addEventListener('click', async function () {
                const formData = new FormData();
                formData.append('email_address', document.querySelector('#email').value);
                formData.append('password', document.querySelector('#password').value);

                try {
                    const response = await fetch(`${API_BASE_URL}/login`, {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Login successful, redirect to homepage
                        localStorage.setItem('email', document.querySelector('#email').value)
                        window.location.href = 'index.html';
                    } else {
                        // Login failed, display error message
                        alert(data.error);
                    }
                } catch (error) {
                    console.error('Error during login:', error);
                    alert('An error occurred during login. Please try again.');
                }
            });
        });
    document
        .getElementById("homeBtn")
        .addEventListener("click", function () {
          window.location.href = "index.html"
        });