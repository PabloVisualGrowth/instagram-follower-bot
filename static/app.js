document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-bot-btn');
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    const resultsArea = document.getElementById('results-area');
    const btnContent = document.querySelector('.btn-content');
    const loader = document.querySelector('.loader');

    runBtn.addEventListener('click', async () => {
        runBtn.disabled = true;
        btnContent.classList.add('hidden');
        loader.classList.remove('hidden');
        statusText.innerText = "Ejecutando bot... por favor espera";
        statusDot.style.backgroundColor = "#ff9800";
        statusDot.style.boxShadow = "0 0 10px #ff9800";

        try {
            const response = await fetch('/run-bot', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                renderResults(data);
                statusText.innerText = "Escaneo completado con exito";
                statusDot.style.backgroundColor = "#00f260";
                statusDot.style.boxShadow = "0 0 10px #00f260";
            } else {
                statusText.innerText = "Error: " + (data.error || "desconocido");
                statusDot.style.backgroundColor = "#ff416c";
                statusDot.style.boxShadow = "0 0 10px #ff416c";
            }
        } catch (error) {
            statusText.innerText = "Error de conexion con el servidor";
            statusDot.style.backgroundColor = "#ff416c";
        } finally {
            runBtn.disabled = false;
            btnContent.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });

    function renderResults(data) {
        resultsArea.classList.remove('hidden');
        document.getElementById('new-count').innerText = data.changes.new_followers.length;
        document.getElementById('unfollow-count').innerText = data.changes.unfollowers.length;
        document.getElementById('total-count').innerText = data.followers.length;

        const list = document.getElementById('followers-list');
        list.innerHTML = '';
        data.followers.sort().forEach((name, i) => {
            const item = document.createElement('div');
            item.className = 'follower-item';
            item.style.animationDelay = `${i * 0.05}s`;
            item.innerHTML = `<strong>${name.charAt(0).toUpperCase()}</strong><span>${name}</span>`;
            list.appendChild(item);
        });

        document.getElementById('screenshot-img').src = `/screenshots/ultimo_scrappeo.png?t=${Date.now()}`;
    }
});
