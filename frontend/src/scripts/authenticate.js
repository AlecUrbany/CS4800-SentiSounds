    
    document.addEventListener('DOMContentLoaded', function () {
        const authenticateButton = document.querySelector('#authenticateButton');
        authenticateButton.addEventListener('click', async function () {
            // Retrieving data from localStorage
            const email = localStorage.getItem('email');

            const formData = new FormData();
            formData.append('email_address', email);
            formData.append('entered_auth_code', document.querySelector('#auth_code').value);
            try {
                const response = await fetch(`${baseURL}/authenticate`, {
                method: 'POST',
                body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Authentication successful. You can now proceed.');
                    window.location.href = "index.html"; // Redirect to index page upon successful authentication
                } else {
                    alert(data.error);
                }
            } catch (error) {
                // console.error('Error during authentication:', error);
                alert("An error occurred during authentication. Please try again.")
            }
        });
    });