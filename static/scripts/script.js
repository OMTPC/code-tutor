// Created by: Orlando Caetano
// Date: [Insert Date]
// Description: This is a file to store JS code that is used in the Code Tutor app, 
// Resources:





// managing the visibility of the scroll indicator
document.addEventListener("DOMContentLoaded", function () {
    const scrollIndicator = document.getElementById("scroll-indicator");

    // Function to check if content overflows the viewport
    function checkOverflow() {
        if (document.documentElement.scrollHeight > window.innerHeight) {
            scrollIndicator.style.display = "block"; 
        } else {
            scrollIndicator.style.display = "none"; 
        }
    }

    // Function to hide the arrow when scrolling
    function hideArrowOnScroll() {
        scrollIndicator.style.display = "none";
        window.removeEventListener("scroll", hideArrowOnScroll); 
    }

    // Run the overflow check on page load
    checkOverflow();
    window.addEventListener("scroll", hideArrowOnScroll);
});

