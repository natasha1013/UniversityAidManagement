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

    // Ensure the submenu of the current section remains open based on the URL
    const currentUrl = window.location.href;
    menuSections.forEach(section => {
        const links = section.querySelectorAll("a");
        let isActive = false;

        links.forEach(link => {
            if (currentUrl.includes(link.getAttribute("href"))) {
                isActive = true;
            }
        });

        // Add or remove the 'active' class based on whether the section matches the current URL
        if (isActive) {
            section.classList.add("active");
        } else {
            section.classList.remove("active");
        }
    });
});