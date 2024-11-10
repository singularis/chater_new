document.addEventListener('DOMContentLoaded', function () {
    // Select all buttons
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('mousedown', function () {
            this.classList.add('clicked');
            // Optional: Remove the class after some time
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 200); // 200 milliseconds
        });
    });

    var textarea = document.getElementById('question');
    textarea.addEventListener('keydown', function (e) {
        // Check if Enter was pressed without Shift key
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent the default action (inserting a new line)
            document.querySelector('.btn[type="submit"]').click(); // Programmatically click the submit button
        }
    });

    // Auto-resize textarea
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';

    textarea.addEventListener('input', function () {
        // Only reset height if the scrollHeight is greater than the current height
        if (this.scrollHeight > this.clientHeight) {
            this.style.height = 'auto'; // Reset height to auto
            this.style.height = this.scrollHeight + 'px'; // Set the height to match the scroll height
        }
    });

    manageCollapsibleBlocks();

    // Observe changes to the container (e.g., when new responses are added)
    const observer = new MutationObserver(manageCollapsibleBlocks);
    const target = document.querySelector('.container');
    const config = { childList: true, subtree: true };

    observer.observe(target, config);
});

function manageCollapsibleBlocks() {
    const headers = document.querySelectorAll('.collapsible-header');
    const contents = document.querySelectorAll('.collapsible-content');

    headers.forEach(header => {
        header.removeEventListener('click', toggleHandler); // Ensure no duplicate listeners
        header.addEventListener('click', toggleHandler);
    });

    // Ensure the first block is expanded by default
    contents.forEach((content, index) => {
        if (index === 0) {
            content.style.display = "block";
            content.style.maxHeight = content.scrollHeight + "px";
        } else {
            content.style.display = "none";
            content.style.maxHeight = "0px";
        }
    });
}

function toggleHandler() {
    const content = this.nextElementSibling;
    const allContents = document.querySelectorAll('.collapsible-content');

    // Collapse all other blocks
    allContents.forEach(otherContent => {
        if (otherContent !== content) {
            otherContent.style.maxHeight = "0px";
            setTimeout(() => {
                otherContent.style.display = "none";
            }, 300);
        }
    });

    // Toggle the clicked block
    if (content.style.maxHeight === "0px" || content.style.display === "none") {
        content.style.display = "block";
        content.style.maxHeight = content.scrollHeight + "px";
    } else {
        content.style.maxHeight = "0px";
        setTimeout(() => {
            content.style.display = "none";
        }, 300);
    }
}