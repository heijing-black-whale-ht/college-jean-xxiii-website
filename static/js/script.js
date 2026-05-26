// Simple JavaScript for the contact form
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            contactForm.reset();
        });
    }
});

// Add some interactive elements
const navLinks = document.querySelectorAll('nav a');
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        // You could add smooth scrolling or other effects here
        console.log('Navigating to:', this.textContent);
    });
});

document.getElementById('hamburger').addEventListener('click', function() {
    let menu = document.getElementById('mobile-menu');

    if (menu.style.display === 'none') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
});
