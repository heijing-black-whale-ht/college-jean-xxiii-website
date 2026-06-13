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

// adding an interactive navigation that appears only when the hamburger menu icon is clicked
// the nav menu appears only if it's not already being displayed
// the nav menu closes when the hamburger menu is clicked a second time
document.getElementById('hamburger').addEventListener('click', function() {
    let menu = document.getElementById('mobile-menu');

    if (menu.style.display === 'none') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
});

// design an interactive wallpaper using different images in static/images
// the collection
const images = [
    "static/images/bg1.png",
    "static/images/bg1 (1).png",
    "static/images/bg1 (2).png",
    "static/images/bg1 (3).png",
    "static/images/bg1 (4).png",
    "static/images/bg1 (5).png"

];

let idx = 0;
const hero = document.getElementById('hero');

function setHeroImage(i) {
    hero.style.backgroundImage = `url('${images[i]}')`;
}

// Set initial image
setHeroImage(idx);

// Rotate every 5 seconds
setIntervall(() => {
    idx = (idx + 1) % images.length;
    setHeroImage(idx);
}, 5000);
