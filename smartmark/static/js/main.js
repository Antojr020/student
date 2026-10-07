document.addEventListener('DOMContentLoaded', () => {
    // Dark Mode Toggle Logic
    const toggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    
    if (currentTheme === 'dark' && toggle) {
        toggle.innerHTML = '<i class="bi bi-brightness-high-fill"></i>';
    }

    if (toggle) {
        toggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', theme);
            localStorage.setItem('theme', theme);
            
            if(theme === 'dark') {
                toggle.innerHTML = '<i class="bi bi-brightness-high-fill"></i>';
            } else {
                toggle.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
            }
        });
    }

    // Initialize Chart.js if canvas exists
    const adminCtx = document.getElementById('adminChart');
    if (adminCtx) {
        new Chart(adminCtx, {
            type: 'bar',
            data: {
                labels: ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5'],
                datasets: [{
                    label: 'Pass Percentage (%)',
                    data: [85, 90, 88, 92, 95],
                    backgroundColor: 'rgba(13, 110, 253, 0.6)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
});
