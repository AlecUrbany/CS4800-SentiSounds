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