// static/js/feedbacks.js

// Function to open a modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

// Function to close a modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Automatically open the reply modal if the tab is set to 'reply'
document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab === 'reply') {
        openModal('reply-modal');
    }
});

// Close modal when clicking outside of it
window.onclick = function (event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function (modal) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};

// Filter feedback rows based on type (all, sent, received)
function filterFeedback(filterType = 'all') {
    const rows = document.querySelectorAll('#feedback-table tbody tr.feedback-row');
    const searchInput = document.getElementById('search-input').value.toLowerCase();

    rows.forEach(row => {
        const type = row.classList.contains('sent') ? 'sent' : 'received';
        const title = row.querySelector('td:nth-child(2)').innerText.toLowerCase();
        const fromTo = row.querySelector('td:nth-child(3)').innerText.toLowerCase();

        // Check if the row matches the filter type and search query
        const matchesFilter = filterType === 'all' || type === filterType;
        const matchesSearch = title.includes(searchInput) || fromTo.includes(searchInput);

        row.style.display = matchesFilter && matchesSearch ? '' : 'none';
    });
}