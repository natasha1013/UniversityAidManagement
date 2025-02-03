document.addEventListener('DOMContentLoaded', function () {
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const targetId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(targetId);
            if (modal) {
                modal.style.display = 'block';
                modal.classList.add('show');
                document.body.classList.add('modal-open');
                modal.setAttribute('aria-modal', 'true');
                modal.removeAttribute('aria-hidden');
            }
        });
    });

    const closeButtons = document.querySelectorAll('.btn-close, [data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');
                modal.setAttribute('aria-hidden', 'true');
                modal.removeAttribute('aria-modal');
            }
        });
    });

    window.addEventListener('click', function (event) {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');
                modal.setAttribute('aria-hidden', 'true');
                modal.removeAttribute('aria-modal');
            }
        });
    });
});