document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-bot-btn');
    const statusText = document.getElementById('status-text');
    const resultsArea = document.getElementById('results-area');
    const btnContent = document.querySelector('.btn-content');
    const loader = document.querySelector('.loader');
    const dot = document.querySelector('.dot');

    const newCount = document.getElementById('new-count');
    const unfollowCount = document.getElementById('unfollow-count');
    const totalCount = document.getElementById('total-count');
    const followersList = document.getElementById('followers-list');
    const screenshotImg = document.getElementById('screenshot-img');

    runBtn.addEventListener('click', async () => {
        // UI State: Running
        runBtn.disabled = true;
        btnContent.classList.add('hidden');
        loader.classList.remove('hidden');
        statusText.innerText = "Ejecutando bot... por favor espera";
        dot.style.backgroundColor = "#ff9800"; // Orange
        dot.style.boxShadow = "0 0 10px #ff9800";

        try {
            const response = await fetch('/run-bot', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                renderResults(data);
                statusText.innerText = "Escaneo completado con éxito";
                dot.style.backgroundColor = "#00f260"; // Green
                dot.style.boxShadow = "0 0 10px #00f260";
            } else {
                statusText.innerText = "Error: " + data.error;
                dot.style.backgroundColor = "#ff416c"; // Red
                dot.style.boxShadow = "0 0 10px #ff416c";
            }
        } catch (error) {
            statusText.innerText = "Error de conexión con el servidor";
            console.error(error);
        } finally {
            runBtn.disabled = false;
            btnContent.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });

    function renderResults(data) {
        resultsArea.classList.remove('hidden');

        // Update stats
        newCount.innerText = data.changes.new_followers.length;
        unfollowCount.innerText = data.changes.unfollowers.length;
        totalCount.innerText = data.followers.length;

        // Update list
        followersList.innerHTML = '';
        data.followers.sort().forEach((name, index) => {
            const item = document.createElement('div');
            item.className = 'follower-item';
            item.style.animationDelay = `${index * 0.05}s`;
            item.innerHTML = `
                <span class="follower-avatar">${name.charAt(0).toUpperCase()}</span>
                <span class="follower-name">${name}</span>
            `;
            followersList.appendChild(item);
        });

        // Update screenshot
        // Add timestamp to prevent caching
        screenshotImg.src = `/screenshots/ultimo_scrappeo.png?t=${new Date().getTime()}`;
    }
});
