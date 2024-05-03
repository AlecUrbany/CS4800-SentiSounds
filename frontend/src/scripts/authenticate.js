    const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');

        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('-translate-x-full');
        });

        document.addEventListener('click', function (e) {
            // Check if click is outside of sidebar and sidebarToggle
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target) && !sidebar.classList.contains('-translate-x-full')) {
                // If sidebar is open and click is outside, close the sidebar
                sidebar.classList.add('-translate-x-full');
            }
        });

        document.addEventListener('DOMContentLoaded', function () {

            const baseURL = 'http://127.0.0.1:5000'; // REPLACE IT WITH BASE URL
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