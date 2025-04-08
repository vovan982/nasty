document.addEventListener('DOMContentLoaded', function() {
    // Preloader
    window.addEventListener('load', function() {
        const preloader = document.querySelector('.preloader');
        preloader.style.opacity = '0';
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    });

    // Header scroll effect
    const header = document.querySelector('.header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Service cards animation
    const serviceCards = document.querySelectorAll('.service-card');
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    serviceCards.forEach(card => {
        observer.observe(card);
    });

    // Add to project functionality
    const addButtons = document.querySelectorAll('.add-to-project');
    let projectCount = localStorage.getItem('projectCount') || 0;

    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const serviceCard = this.closest('.service-card');
            const serviceName = serviceCard.querySelector('h2').textContent;
            const servicePrice = serviceCard.querySelector('.price').textContent;

            // Add to localStorage
            let project = JSON.parse(localStorage.getItem('project')) || [];
            project.push({
                name: serviceName,
                price: servicePrice
            });
            localStorage.setItem('project', JSON.stringify(project));

            // Update counter
            projectCount++;
            localStorage.setItem('projectCount', projectCount);

            // Update button state
            this.textContent = 'Добавлено в проект';
            this.classList.add('added');
            this.disabled = true;

            // Show notification
            showNotification('Услуга добавлена в проект');
        });
    });

    // Notification function
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}); 