document.addEventListener('DOMContentLoaded', () => {
    // Инициализация счетчика в localStorage
    if (!localStorage.getItem('serviceCounter')) {
        localStorage.setItem('serviceCounter', '0');
    }

    // Обновление счетчика на плавающей кнопке
    const updateCounter = () => {
        const counter = document.querySelector('.floating-btn__counter');
        if (counter) {
            counter.textContent = localStorage.getItem('serviceCounter');
        }
    };

    // Обработка кликов по карточкам услуг
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.btn')) {
                const link = card.querySelector('.btn');
                if (link) {
                    link.click();
                }
            }
        });
    });

    // Обработка клика по плавающей кнопке
    const floatingBtn = document.querySelector('.floating-btn');
    if (floatingBtn) {
        floatingBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const currentCount = parseInt(localStorage.getItem('serviceCounter'));
            localStorage.setItem('serviceCounter', (currentCount + 1).toString());
            updateCounter();
            // Здесь можно добавить логику для открытия формы или модального окна
            alert('Спасибо за интерес к нашим услугам! Мы свяжемся с вами в ближайшее время.');
        });
    }

    // Анимация появления карточек при прокрутке
    const animateCards = () => {
        const cards = document.querySelectorAll('.service-card');
        cards.forEach((card, index) => {
            const cardTop = card.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (cardTop < windowHeight - 100) {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 200);
            }
        });
    };

    // Добавление стилей для анимации
    const style = document.createElement('style');
    style.textContent = `
        .service-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
    `;
    document.head.appendChild(style);

    // Инициализация
    updateCounter();
    animateCards();
    window.addEventListener('scroll', animateCards);

    // DOM Elements
    const floatingBtnCounter = document.querySelector('.floating-btn__counter');

    // Intersection Observer for service cards animation
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe service cards
    serviceCards.forEach(card => {
        observer.observe(card);
    });

    // Local Storage for selected services
    let selectedServices = JSON.parse(localStorage.getItem('selectedServices')) || [];

    // Update floating button counter
    function updateCounter() {
        const count = selectedServices.length;
        floatingBtnCounter.textContent = count;
        floatingBtn.style.display = count > 0 ? 'flex' : 'none';
    }

    // Handle service card clicks
    serviceCards.forEach(card => {
        card.addEventListener('click', () => {
            const serviceId = card.dataset.serviceId;
            const serviceTitle = card.querySelector('h2').textContent;
            
            if (selectedServices.some(service => service.id === serviceId)) {
                selectedServices = selectedServices.filter(service => service.id !== serviceId);
            } else {
                selectedServices.push({ id: serviceId, title: serviceTitle });
            }
            
            localStorage.setItem('selectedServices', JSON.stringify(selectedServices));
            updateCounter();
            
            // Visual feedback
            card.classList.toggle('selected');
        });
    });

    // Initialize counter
    updateCounter();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form submission handling
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());
            
            try {
                // Here you would typically send the data to your server
                console.log('Form data:', data);
                
                // Show success message
                alert('Спасибо за вашу заявку! Мы свяжемся с вами в ближайшее время.');
                contactForm.reset();
                
            } catch (error) {
                console.error('Error submitting form:', error);
                alert('Произошла ошибка при отправке формы. Пожалуйста, попробуйте позже.');
            }
        });
    }

    // Add loading animation for images
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('load', () => {
            img.classList.add('loaded');
        });
    });

    // Floating button counter
    let viewCount = localStorage.getItem('viewCount') || 0;
    viewCount++;
    localStorage.setItem('viewCount', viewCount);
    floatingBtnCounter.textContent = viewCount;

    // Add hover effect to service cards
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });

    // Add click event to floating button
    floatingBtn.addEventListener('click', () => {
        const contactSection = document.querySelector('#contact');
        if (contactSection) {
            contactSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
}); 