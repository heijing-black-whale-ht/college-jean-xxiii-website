document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');

    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            // Stop the native browser POST submit action
            event.preventDefault();
            
            // Pop up the message box
            alert('MESSAGE ENVOYÉ');
            
            // Wipe the inputs clean
            this.reset();
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const modalElement = document.getElementById('legalGatekeeperModal');
    
    // Safety Guard: Stop the modal execution if the elements don't exist on the current page
    if (!modalElement) return;

    // CRITICAL: If the visitor is explicitly on the legal page to read it, 
    // do not show the gatekeeper modal, otherwise they are trapped in an infinite loop.
    if (window.location.pathname === "/terms" || window.location.pathname === "/terms/") {
        return;
    }

    // Initialize the Bootstrap Modal Instance
    const gatekeeperModal = new bootstrap.Modal(modalElement, {
        backdrop: 'static',
        keyboard: false
    });

    // Check if the user has already validated this step previously
    const hasAccepted = localStorage.getItem('legalValidationToken');

    if (!hasAccepted) {
        gatekeeperModal.show();
    }

    // Event Listener: Action on Accept Button Click
    document.getElementById('gatekeeperAccept').addEventListener('click', function () {
        // Drop a validation marker inside the user's browser memory
        localStorage.setItem('legalValidationToken', 'approved_2026');
        gatekeeperModal.hide();
    });

    // Event Listener: Action on Refuse Button Click
    document.getElementById('gatekeeperRefuse').addEventListener('click', function () {
        alert("Accès refusé. Vous devez accepter les termes d'utilisation pour naviguer sur le site du collège.");
        // Hard reload the current view to keep the gate locked tightly
        window.location.reload();
    });
});

// ============================================================================
// SEARCH FUNCTIONALITY
// ============================================================================
document.addEventListener("DOMContentLoaded", function () {
    const searchToggle = document.getElementById('searchToggle');
    const searchBarContainer = document.getElementById('searchBarContainer');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    // Website content that can be searched
    const searchableContent = [
        { title: 'Accueil', url: '/', section: 'Pages principales' },
        { title: 'À Propos', url: '/about', section: 'Pages principales' },
        { title: 'Évènements', url: '/events', section: 'Pages principales' },
        { title: 'Contacts', url: '/contact', section: 'Pages principales' },
        { title: 'Termes et Conditions', url: '/terms', section: 'Légal' },
        { title: 'Politique de Confidentialité', url: '/terms#privacy', section: 'Légal' }
    ];

    // Toggle search bar visibility
    searchToggle.addEventListener('click', function (e) {
        e.preventDefault();
        const isVisible = searchBarContainer.style.display !== 'none';
        searchBarContainer.style.display = isVisible ? 'none' : 'block';
        if (!isVisible) {
            searchInput.focus();
            searchResults.innerHTML = '';
        }
    });

    // Search functionality
    searchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase().trim();
        searchResults.innerHTML = '';

        if (query.length === 0) {
            return;
        }

        const matches = searchableContent.filter(item =>
            item.title.toLowerCase().includes(query) ||
            item.section.toLowerCase().includes(query)
        );

        if (matches.length === 0) {
            searchResults.innerHTML = '<p class="small text-muted p-2">Aucun résultat trouvé</p>';
            return;
        }

        const resultsList = document.createElement('div');
        resultsList.className = 'list-group list-group-flush';

        matches.forEach(match => {
            const resultItem = document.createElement('a');
            resultItem.href = match.url;
            resultItem.className = 'list-group-item list-group-item-action bg-dark text-light border-secondary small';
            resultItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${match.title}</strong>
                        <div class="text-muted" style="font-size: 0.85rem;">${match.section}</div>
                    </div>
                </div>
            `;
            resultItem.addEventListener('click', function () {
                searchBarContainer.style.display = 'none';
            });
            resultsList.appendChild(resultItem);
        });

        searchResults.appendChild(resultsList);
    });

    // Close search bar when pressing ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && searchBarContainer.style.display !== 'none') {
            searchBarContainer.style.display = 'none';
            searchInput.value = '';
            searchResults.innerHTML = '';
        }
    });

    // Close search bar when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchBarContainer.contains(e.target) && !searchToggle.contains(e.target)) {
            searchBarContainer.style.display = 'none';
            searchInput.value = '';
            searchResults.innerHTML = '';
        }
    });
});
