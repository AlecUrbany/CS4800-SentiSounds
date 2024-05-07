 document
        .getElementById("loginButton")
        .addEventListener("click", function () {
          window.location.href = "login.html"
        });
        document
        .getElementById("homeBtn")
        .addEventListener("click", function () {
          window.location.href = "index.html"
        });

        document.addEventListener('DOMContentLoaded', function () {
            const signupButton = document.querySelector('#signupButton');

            signupButton.addEventListener('click', async function () {

                const email = document.querySelector('#email').value;
                const firstName = document.querySelector('#username').value;
                const lastInitial = document.querySelector('#last_initial').value;
                const password = document.querySelector('#password').value;
                const confirmPassword = document.querySelector('#confirm_password').value;

                // Check if all fields are filled
                if (!email || !password || !confirmPassword || !firstName || !lastInitial) {
                    alert('Please fill in all fields.');
                    return;
                }

                // Email validation
                if (!/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email)) {
                    alert('Please enter a valid email address.');
                    return;
                }

                // First name check
                if(firstName.length > 29) {
                    alert('First name is too long.')
                    return;
                }

                // Last initial check
                if (lastInitial.length < 1) {
                    alert('Last initial must be only one character.')
                    return;
                }

                // Password length check
                if (password.length < 6) {
                    alert('Password must be at least 7 characters long.');
                    return;
                }
                
                // Check if passwords match
                if (password !== confirmPassword) {
                    alert('Passwords do not match. Please try again.');
                    return; 
                }
                // Storing data in localStorage
                localStorage.setItem('email', email);
                localStorage.setItem('firstName', firstName);
                localStorage.setItem('lastInitial', lastInitial);

                const formData = new FormData();
                formData.append('email_address', document.querySelector('#email').value);
                formData.append('password', document.querySelector('#password').value);
                formData.append('first_name', document.querySelector('#username').value);
                formData.append('last_initial', document.querySelector('#last_initial').value);

                try {
                    const response = await fetch(`${baseURL}/sign-up`, {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok) {
                        alert('Signup successful. Please check your email for further instructions.');
                        // Redirect to authenticate.html
                        window.location.href = "authenticate.html";
                    } else {
                        alert(data.error);
                    }
                } catch (error) {
                    console.error('Error during signup:', error);
                    alert("An error occurred during signup. Please try again.")
                }
            });
        });
