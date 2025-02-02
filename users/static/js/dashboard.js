document.addEventListener("DOMContentLoaded", function () {
    // Get all menu sections
    const menuSections = document.querySelectorAll(".menu-section");

    // Add click event listeners to each h1
    menuSections.forEach(section => {
        const heading = section.querySelector("h1");
        heading.addEventListener("click", () => {
            // Close all other sections
            menuSections.forEach(otherSection => {
                if (otherSection !== section) {
                    otherSection.classList.remove("active");
                }
            });

            // Toggle the clicked section
            section.classList.toggle("active");
        });
    });
});