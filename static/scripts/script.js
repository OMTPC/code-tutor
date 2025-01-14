document.addEventListener("DOMContentLoaded", function () {
    const scrollIndicator = document.getElementById("scroll-indicator");

    // Function to check if content overflows the viewport
    function checkOverflow() {
        if (document.documentElement.scrollHeight > window.innerHeight) {
            scrollIndicator.style.display = "block"; // Show the down arrow
        } else {
            scrollIndicator.style.display = "none"; // Hide it if no overflow
        }
    }

    // Function to hide the arrow when scrolling
    function hideArrowOnScroll() {
        scrollIndicator.style.display = "none";
        window.removeEventListener("scroll", hideArrowOnScroll); // Remove the event to prevent repeated execution
    }

    // Run the overflow check on page load
    checkOverflow();

    // Add a scroll listener to hide the arrow
    window.addEventListener("scroll", hideArrowOnScroll);
});

