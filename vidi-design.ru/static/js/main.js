let projectItems = [];
const projectButton = document.getElementById('projectButton');
const projectCount = document.getElementById('projectCount');
const addButtons = document.querySelectorAll('.add-to-project');

function updateProjectButton() {
    projectCount.textContent = projectItems.length;
    if (projectItems.length > 0) {
        projectButton.style.display = 'flex';
    } else {
        projectButton.style.display = 'none';
    }
}

addButtons.forEach(button => {
    button.addEventListener('click', function() {
        const service = this.dataset.service;
        const price = this.dataset.price;
        
        if (this.classList.contains('added')) {
            // Remove from project
            projectItems = projectItems.filter(item => item.service !== service);
            this.classList.remove('added');
            this.textContent = '+ Добавить в проект';
        } else {
            // Add to project
            projectItems.push({ service, price });
            this.classList.add('added');
            this.textContent = '✓ В проекте';
        }
        
        updateProjectButton();
        
        // Save to localStorage
        localStorage.setItem('projectItems', JSON.stringify(projectItems));
    });
});

projectButton.addEventListener('click', function() {
    if (projectItems.length > 0) {
        const total = projectItems.reduce((sum, item) => sum + parseInt(item.price), 0);
        const message = 'Ваш проект:\n\n' + 
            projectItems.map(item => `${item.service} - ${item.price} руб`).join('\n') + 
            '\n\nОбщая стоимость: ' + total + ' руб';
            
        // Можно добавить отправку на сервер или другое действие
        alert(message);
    }
});

// Load saved items from localStorage
window.addEventListener('load', function() {
    const savedItems = localStorage.getItem('projectItems');
    if (savedItems) {
        projectItems = JSON.parse(savedItems);
        updateProjectButton();
        
        // Update buttons state
        projectItems.forEach(item => {
            const button = Array.from(addButtons).find(btn => btn.dataset.service === item.service);
            if (button) {
                button.classList.add('added');
                button.textContent = '✓ В проекте';
            }
        });
    } else {
        projectButton.style.display = 'none';
    }
}); 