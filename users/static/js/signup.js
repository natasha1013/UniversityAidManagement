document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.querySelector("select[name='role']");
    const step1 = document.getElementById("step-1");
    const step2 = document.getElementById("step-2");
    const continueBtn = document.getElementById("continue-btn");
    const previousBtn = document.getElementById("previous-btn");
    const submitBtn = document.getElementById("submit-btn");

    const studentFields = document.getElementById("student-fields");
    const funderFields = document.getElementById("funder-fields");
    const officerFields = document.getElementById("officer-fields");

    const allRoleFields = [studentFields, funderFields, officerFields];

    function toggleFields() {
        let selectedRole = roleSelect.value;

        // Hide all role-specific fields
        allRoleFields.forEach(field => {
            field.style.display = "none";
            field.querySelectorAll("input").forEach(input => {
                input.disabled = true;
                input.removeAttribute("required");
            });
        });

        // Show only the relevant fields
        let activeFields = selectedRole === "student" ? studentFields :
                           selectedRole === "funder" ? funderFields :
                           selectedRole === "officer" ? officerFields : null;

        if (activeFields) {
            activeFields.style.display = "block";
            activeFields.querySelectorAll("input").forEach(input => {
                input.disabled = false;
                input.setAttribute("required", "true");
            });
        }
    }

    // Move to step 2
    continueBtn.addEventListener("click", function (e) {
        e.preventDefault();
        toggleFields();
        step1.style.display = "none";
        step2.style.display = "block";
    });

    // Go back to step 1
    previousBtn.addEventListener("click", function (e) {
        e.preventDefault();
        step2.style.display = "none";
        step1.style.display = "block";
    });

    // Ensure role fields are updated when role changes
    roleSelect.addEventListener("change", toggleFields);

    // Initialize
    step2.style.display = "none";
});
