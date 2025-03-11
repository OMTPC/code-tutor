// Created by: Orlando Caetano
// Last updated: 18/02/2025
// Description: This is a file to store JS code that is used in the Code Mentor app, 
// Resources: Please refer to References.txt for the resources used to build this application.


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

