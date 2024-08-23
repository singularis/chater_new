document.addEventListener('DOMContentLoaded', function() {
    // Select all buttons
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.classList.add('clicked');
            // Optional: Remove the class after some time
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 200); // 200 milliseconds
        });
    });

    var textarea = document.getElementById('question');
    textarea.addEventListener('keydown', function(e) {
        // Check if Enter was pressed without Shift key
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent the default action (inserting a new line)
            document.querySelector('.btn[type="submit"]').click(); // Programmatically click the submit button
        }
    });

    // Auto-resize textarea
    var textarea = document.getElementById('question');

    // Set the initial height based on the content
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';

    // Auto-resize textarea without flickering
    textarea.addEventListener('input', function() {
        // Only reset height if the scrollHeight is greater than the current height
        if (this.scrollHeight > this.clientHeight) {
            this.style.height = 'auto'; // Reset height to auto
            this.style.height = this.scrollHeight + 'px'; // Set the height to match the scroll height
        }
    });
});

function toggleContent(element) {
    const content = element.nextElementSibling;
    if (content.style.display === "none" || content.style.display === "") {
        content.style.display = "block";
        content.style.maxHeight = "2000px"; // Set expanded height to 2000px
    } else {
        content.style.display = "none";
        content.style.maxHeight = "200px"; // Set collapsed height to 200px
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const contents = document.querySelectorAll('.collapsible-content');
    contents.forEach((content, index) => {
        if (index === 0) {  // Expand the first content box by default
            content.style.display = "block";
            content.style.maxHeight = "2000px"; // Expanded height for the first box
        } else {
            content.style.display = "none";  // Collapse all others
            content.style.maxHeight = ""; // Remove fixed height to allow auto-resize
        }
    });
});