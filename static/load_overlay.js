function createOverlay(messageContent) {
    // Create the overlay element
    var overlay = document.getElementById('load_container');
    var message = document.getElementById('message_box');
    if (overlay) {
        overlay.style.display = 'flex';
        if (message) {
            message.textContent = messageContent;
        }
        return
    }
    
    var load_container = document.createElement('div');
    load_container.id = 'load_container'

    // Style the overlay to cover the entire screen
    load_container.style.position = 'fixed';
    load_container.style.top = 0;
    load_container.style.left = 0;
    load_container.style.width = '100%';
    load_container.style.height = '100%';
    load_container.style.backgroundColor = 'rgba(255, 255, 255, 0.5)'; // Black color with 50% opacity
    load_container.style.zIndex = 1000; // Ensure it covers other elements

    load_container.style.display = 'flex';
    load_container.style.justifyContent = 'center'; // Center horizontally
    load_container.style.alignItems = 'center'; // Center vertically
    load_container.style.flexDirection = 'column';

    var spinnerIcon = document.createElement('i');
    spinnerIcon.classList.add('fas', 'fa-circle-notch', 'fa-spin', 'fa-3x');
    load_container.appendChild(spinnerIcon);
    document.body.appendChild(load_container);

    var textElement = document.createElement('div');
    textElement.id = 'message_box'
    textElement.textContent = messageContent;
    textElement.style.marginTop = '10px';
    textElement.style.fontFamily = 'Arial'
    textElement.style.fontWeight = 'bold' // Add some margin from the spinner
    load_container.appendChild(textElement);
}
function destroyOverlay(messageContent, color = 'black') {
    // Get the overlay element by ID
    var overlay = document.getElementById('load_container');
    var message = document.getElementById('message_box');
    
    // If the overlay exists, hide it
    if (message) {
        message.textContent = messageContent;
        message.style.color = color;
    }

    if (overlay) {
        setTimeout(function() {
            overlay.style.display = 'none';
        }, 800)
    }
}
