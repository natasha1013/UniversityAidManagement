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
