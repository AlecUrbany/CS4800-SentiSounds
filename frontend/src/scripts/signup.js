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
            const baseURL = 'http://127.0.0.1:5000'; // REPLACE IT WITH BASE URL

            const signupButton = document.querySelector('#signupButton');


            signupButton.addEventListener('click', async function () {

                const email = document.querySelector('#email').value;
                const password = document.querySelector('#password').value;
                const firstName = document.querySelector('#username').value;
                const lastInitial = document.querySelector('#last_initial').value;


                // Storing data in localStorage
                localStorage.setItem('email', email);


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
                        // Get user input values
                        const email = document.querySelector('#email').value;
                        const password = document.querySelector('#password').value;
                        const firstName = document.querySelector('#username').value;
                        const lastInitial = document.querySelector('#last_initial').value;


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

