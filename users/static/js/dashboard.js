document.addEventListener('DOMContentLoaded', function () {
    // Open modal when a trigger button is clicked
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const targetId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(targetId);
            if (modal) {
                modal.style.display = 'block'; // Show the modal
                modal.classList.add('show'); // Add 'show' class to make it visible
                document.getElementById('modalBackdrop').style.display = 'block'; // Show the backdrop
            }
        });
    });

    // Close modal when the close button (X) or Cancel button is clicked
    const closeButtons = document.querySelectorAll('.custom-close-btn, .btn-secondary');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            closeModal(); // Call the helper function to close the modal
        });
    });

    // Close modal when clicking outside the modal content (on the backdrop)
    window.addEventListener('click', function (event) {
        const modal = document.querySelector('.custom-modal.show');
        if (event.target === modal || event.target.id === 'modalBackdrop') {
            closeModal(); // Call the helper function to close the modal
        }
    });

    // Helper function to close the modal
    function closeModal() {
        const modal = document.querySelector('.custom-modal.show');
        if (modal) {
            modal.style.display = 'none'; // Hide the modal
            modal.classList.remove('show'); // Remove the 'show' class
            document.getElementById('modalBackdrop').style.display = 'none'; // Hide the backdrop
        }
    }

    // Attach closeModal to the global window object
    window.closeModal = closeModal;

    // Add event listeners to all "Edit" buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', async function () {
            const userId = this.getAttribute('data-user-id');
            // Fetch user data from the API
            const user = await fetchUserData(userId);
            if (user) {
                setTimeout(() => populateModal(user), 100);
            }
        });
    });
});

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
    console.log("Populating modal with user data:", user);
    // Populate common fields
    document.getElementById('userId').value = user.id;
    document.getElementById('modal-username').value = user.username;
    document.getElementById('modal-first_name').value = user.first_name || '';
    document.getElementById('modal-last_name').value = user.last_name || '';
    document.getElementById('modal-email').value = user.email || '';
    document.getElementById('modal-phone_number').value = user.phone_number || '';

    // Clear and hide role-specific fields
    document.getElementById('studentFields').style.display = 'none';
    document.getElementById('funderFields').style.display = 'none';

    // Show fields based on role
    if (user.role === 'student') {
        document.getElementById('studentFields').style.display = 'block';
        document.getElementById('modal-study_program').value = user.study_program || '';
        document.getElementById('modal-years_of_study').value = user.years_of_study || '';
        document.getElementById('modal-gpa').value = user.gpa || '';
    } else if (user.role === 'funder') {
        document.getElementById('funderFields').style.display = 'block';
        document.getElementById('modal-organization_name').value = user.organization_name || '';
    }

    // Update the form action URL to include the user ID
    const form = document.getElementById('editUserForm');
    form.action = `update-user/${user.id}/`;
}