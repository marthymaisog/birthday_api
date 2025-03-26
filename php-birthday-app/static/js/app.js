document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('birthdayForm');
    const birthdayList = document.getElementById('birthdayList');
    
    // Load birthdays when page loads
    fetchBirthdays();
    
    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const dob = document.getElementById('dob').value;
        
        try {
            const response = await fetch(`/hello/${username}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dateOfBirth: dob })
            });
            
            if (response.status === 204) {
                alert('Birthday saved successfully!');
                form.reset();
                fetchBirthdays();
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            alert('Failed to save birthday');
        }
    });
    
    // Fetch and display birthdays
    async function fetchBirthdays() {
        try {
            const response = await fetch('/users');
            const data = await response.json();
            
            birthdayList.innerHTML = data.map(user => `
                <div class="birthday-item">
                    <span>${user.username}</span>
                    <span>${user.date_of_birth}</span>
                </div>
            `).join('');
        } catch (error) {
            birthdayList.innerHTML = 'Error loading birthdays';
        }
    }
});