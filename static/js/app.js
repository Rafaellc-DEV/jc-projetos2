document.addEventListener('DOMContentLoaded', function() {

    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-toggle-icon');
    const docHtml = document.documentElement; // <html> tag

    // Função para aplicar o tema e atualizar o ícone
    function applyTheme(theme) {
        if (theme === 'dark') {
            docHtml.setAttribute('data-theme', 'dark');
            if (themeIcon) themeIcon.className = 'bi bi-sun';
            localStorage.setItem('theme', 'dark');
        } else {
            docHtml.setAttribute('data-theme', 'light');
            if (themeIcon) themeIcon.className = 'bi bi-moon';
            localStorage.setItem('theme', 'light');
        }
    }

    // Função para alternar o tema
    function toggleTheme() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    }

    // 1. Carregar o tema salvo no localStorage
    const savedTheme = localStorage.getItem('theme');
    
    // 2. Ou verificar a preferência do OS
    const osPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

    // 3. Aplicar o tema inicial (Salvo > OS > Padrão 'light')
    applyTheme(savedTheme || osPreference);

    // 4. Adicionar o evento de clique no botão
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});