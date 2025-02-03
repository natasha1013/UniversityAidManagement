// Function to fetch user data from the API
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/`);
        if (!response.ok) {
            throw new Error('Failed to load user data.');
        }
        return await response.json();
    } catch (error) {
        alert(error.message);
        return null;
    }
}

// Function to populate the modal with user data
function populateModal(user) {
    // Populate common fields
    document.getElementById('userId').value = user.id;
    document.getElementById('username').value = user.username;
    document.getElementById('first_name').value = user.first_name || '';
    document.getElementById('last_name').value = user.last_name || '';
    document.getElementById('email').value = user.email || '';
    document.getElementById('phone_number').value = user.phone_number || '';

    // Clear and hide role-specific fields
    document.getElementById('studentFields').style.display = 'none';
    document.getElementById('funderFields').style.display = 'none';

    // Show fields based on role
    if (user.role === 'student') {
        document.getElementById('studentFields').style.display = 'block';
        document.getElementById('study_program').value = user.study_program || '';
        document.getElementById('years_of_study').value = user.years_of_study || '';
        document.getElementById('gpa').value = user.gpa || '';
    } else if (user.role === 'funder') {
        document.getElementById('funderFields').style.display = 'block';
        document.getElementById('organization_name').value = user.organization_name || '';
    }

    // Update the form action URL to include the user ID
    const form = document.getElementById('editUserForm');
    form.action = `update-user/${user.id}/`;
}

// Event listener for DOMContentLoaded
document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners to all "Edit" buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', async function () {
            const userId = this.getAttribute('data-user-id');

            // Fetch user data from the API
            const user = await fetchUserData(userId);
            if (user) {
                populateModal(user);
            }
        });
    });
});