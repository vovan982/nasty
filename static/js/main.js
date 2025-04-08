document.addEventListener('DOMContentLoaded', () => {
    // Initialize service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/flutter_service_worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    }

    // Initialize localStorage for project counter
    if (!localStorage.getItem('projectCounter')) {
        localStorage.setItem('projectCounter', '0');
    }

    // Update floating button counter
    const updateCounter = () => {
        const counter = document.querySelector('.floating-btn__counter');
        if (counter) {
            counter.textContent = localStorage.getItem('projectCounter');
        }
    };

    // Handle project selection
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        const selectBtn = card.querySelector('.btn');
        if (selectBtn) {
            selectBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const currentCount = parseInt(localStorage.getItem('projectCounter'));
                localStorage.setItem('projectCounter', (currentCount + 1).toString());
                updateCounter();
                
                // Show success message
                const successMsg = document.createElement('div');
                successMsg.className = 'success-message';
                successMsg.textContent = 'Проект добавлен в корзину';
                document.body.appendChild(successMsg);
                
                setTimeout(() => {
                    successMsg.remove();
                }, 3000);
            });
        }
    });

    // Initialize counter on page load
    updateCounter();

    // DOM Elements
    const header = document.querySelector('.header');
    const navLinks = document.querySelectorAll('.nav__list a');
    const floatingBtn = document.querySelector('.floating-btn');

    // Scroll event for header
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            // Scroll down
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            // Scroll up
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
    });

    // Active nav link
    function setActiveLink() {
        const sections = document.querySelectorAll('section');
        const scrollPosition = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', setActiveLink);

    // Smooth scroll for nav links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            window.scrollTo({
                top: targetSection.offsetTop - 80,
                behavior: 'smooth'
            });
        });
    });

    // Service cards animation
    function animateServiceCards() {
        const triggerBottom = window.innerHeight * 0.8;
        
        serviceCards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            
            if (cardTop < triggerBottom) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    }

    // Initial animation for service cards
    serviceCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    window.addEventListener('scroll', animateServiceCards);
    window.addEventListener('load', animateServiceCards);

    // Floating button functionality
    let clickCount = 0;
    floatingBtn.addEventListener('click', () => {
        clickCount++;
        const counter = floatingBtn.querySelector('.floating-btn__counter');
        counter.textContent = clickCount;
        
        // Animate button
        floatingBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            floatingBtn.style.transform = 'scale(1)';
        }, 100);
    });

    // Save click count to localStorage
    window.addEventListener('beforeunload', () => {
        localStorage.setItem('clickCount', clickCount);
    });

    // Load click count from localStorage
    window.addEventListener('load', () => {
        const savedCount = localStorage.getItem('clickCount');
        if (savedCount) {
            clickCount = parseInt(savedCount);
            const counter = floatingBtn.querySelector('.floating-btn__counter');
            counter.textContent = clickCount;
        }
    });

    // Intersection Observer for project info items
    const projectInfoItems = document.querySelectorAll('.project-info__item');
    const observerOptions = {
        threshold: 0.2
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    projectInfoItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(item);
    });

    // Header scroll effect
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Animate elements on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.service-card, .project-info__item');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight) && (elementBottom > 0);
            
            if (isVisible) {
                element.classList.add('visible');
            }
        });
    };

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Initial check

    // Smooth scroll for navigation links
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

    // Floating button functionality
    const floatingBtn = document.querySelector('.floating-btn');
    if (floatingBtn) {
        let clickCount = localStorage.getItem('floatingBtnClicks') || 0;
        const counter = floatingBtn.querySelector('.floating-btn__counter');
        
        if (counter) {
            counter.textContent = clickCount;
        }

        floatingBtn.addEventListener('click', () => {
            clickCount++;
            localStorage.setItem('floatingBtnClicks', clickCount);
            if (counter) {
                counter.textContent = clickCount;
            }
            
            // Add animation effect
            floatingBtn.style.transform = 'scale(1.2)';
            setTimeout(() => {
                floatingBtn.style.transform = 'scale(1)';
            }, 200);
        });
    }

    // Service cards hover effect
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Mobile menu toggle (if needed)
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navList = document.querySelector('.nav__list');
    
    if (mobileMenuBtn && navList) {
        mobileMenuBtn.addEventListener('click', () => {
            navList.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }
}); 