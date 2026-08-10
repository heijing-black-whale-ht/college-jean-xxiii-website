document.addEventListener('DOMContentLoaded', function () {
    const contactForm = document.getElementById('contact-form') || document.getElementById('contact-form-bypass');

    if (contactForm) {
        contactForm.addEventListener('submit', function (event) {
            event.preventDefault();
            alert('MESSAGE ENVOYÉ');
            this.reset();
        });
    }

    const modalElement = document.getElementById('legalGatekeeperModal');
    if (modalElement) {
        const path = window.location.pathname;
        const isTermsPage = path === '/terms' || path === '/terms/' || path === '/terms.html';
        if (!isTermsPage) {
            const hasAccepted = localStorage.getItem('legalValidationToken');
            if (!hasAccepted) {
                modalElement.classList.remove('hidden');
            }

            const acceptBtn = document.getElementById('gatekeeperAccept');
            const refuseBtn = document.getElementById('gatekeeperRefuse');
            const backdrop = modalElement.querySelector('[data-close-modal="true"]');

            const closeModal = () => {
                modalElement.classList.add('hidden');
                modalElement.setAttribute('aria-hidden', 'true');
            };

            if (acceptBtn) {
                acceptBtn.addEventListener('click', function () {
                    localStorage.setItem('legalValidationToken', 'approved_2026');
                    closeModal();
                });
            }

            if (refuseBtn) {
                refuseBtn.addEventListener('click', function () {
                    alert("Accès refusé. Vous devez accepter les termes d'utilisation pour naviguer sur le site du collège.");
                    window.location.reload();
                });
            }

            if (backdrop) {
                backdrop.addEventListener('click', closeModal);
            }
        }
    }

    const searchToggle = document.getElementById('searchToggle');
    const searchBarContainer = document.getElementById('searchBarContainer');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const hamburger = document.getElementById('hamburger');
    const navbarNav = document.getElementById('navbarNav');

    if (hamburger && navbarNav) {
        hamburger.addEventListener('click', function () {
            navbarNav.classList.toggle('hidden');
        });
    }

    if (searchToggle && searchBarContainer && searchInput && searchResults) {
        const searchableContent = [
            { title: 'Accueil', url: '/', section: 'Pages principales' },
            { title: 'À Propos', url: '/about', section: 'Pages principales' },
            { title: 'Évènements', url: '/events', section: 'Pages principales' },
            { title: 'Contacts', url: '/contact', section: 'Pages principales' },
            { title: 'Termes et Conditions', url: '/terms', section: 'Légal' },
            { title: 'Politique de Confidentialité', url: '/terms#privacy', section: 'Légal' }
        ];

        searchToggle.addEventListener('click', function (event) {
            event.preventDefault();
            const isHidden = searchBarContainer.classList.contains('hidden');
            searchBarContainer.classList.toggle('hidden');
            if (!isHidden) {
                searchInput.focus();
                searchResults.innerHTML = '';
            }
        });

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
                searchResults.innerHTML = '<p class="p-2 text-sm text-slate-400">Aucun résultat trouvé</p>';
                return;
            }

            const resultsList = document.createElement('div');
            resultsList.className = 'space-y-2';

            matches.forEach(match => {
                const resultItem = document.createElement('a');
                resultItem.href = match.url;
                resultItem.className = 'block rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 transition hover:border-red-500 hover:text-white';
                resultItem.innerHTML = `
                    <div class="font-semibold text-white">${match.title}</div>
                    <div class="mt-1 text-xs text-slate-400">${match.section}</div>
                `;
                resultItem.addEventListener('click', function () {
                    searchBarContainer.classList.add('hidden');
                });
                resultsList.appendChild(resultItem);
            });

            searchResults.appendChild(resultsList);
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !searchBarContainer.classList.contains('hidden')) {
                searchBarContainer.classList.add('hidden');
                searchInput.value = '';
                searchResults.innerHTML = '';
            }
        });

        document.addEventListener('click', function (event) {
            if (!searchBarContainer.contains(event.target) && !searchToggle.contains(event.target)) {
                searchBarContainer.classList.add('hidden');
                searchInput.value = '';
                searchResults.innerHTML = '';
            }
        });
    }
});
