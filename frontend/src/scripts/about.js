        document
        .getElementById("homeBtn")
        .addEventListener("click", function () {
          window.location.href = "index.html"
        });

         const ctx = document.getElementById('skillsChart').getContext('2d');
    const skillsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Python', 'JavaScript', 'HTML/CSS'],
            datasets: [{
                label: 'Skills',
                data: [60, 20, 20],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: false,  // Disable responsiveness
            maintainAspectRatio: false,  // Disable aspect ratio maintenance
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });