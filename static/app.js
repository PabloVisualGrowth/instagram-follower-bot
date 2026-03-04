// ── State ────────────────────────────────────────────────────
let lastNewFollowers = [];

// ── Tab Navigation ────────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
});

// ── Helpers ────────────────────────────────────────────────────
function setStatus(elId, dotId, text, dotClass) {
    document.getElementById(elId).textContent = text;
    const dot = document.getElementById(dotId).previousElementSibling;
    dot.className = `dot ${dotClass}`;
}

function setBtn(btn, loading) {
    btn.querySelector('.btn-label').classList.toggle('hidden', loading);
    btn.querySelector('.spinner').classList.toggle('hidden', !loading);
    btn.disabled = loading;
}

function renderUserList(containerId, users, badgeClass, badgeText) {
    const el = document.getElementById(containerId);
    if (!users || users.length === 0) {
        el.innerHTML = `<div class="empty-msg">Ninguno</div>`;
        return;
    }
    el.innerHTML = users.map((u, i) => `
        <div class="user-item" style="animation-delay:${i * 0.04}s">
            <span class="badge ${badgeClass}">${badgeText}</span>
            <span>@${u}</span>
        </div>`).join('');
}

// ── TRACKER ────────────────────────────────────────────────────
document.getElementById('scan-btn').addEventListener('click', async () => {
    const btn = document.getElementById('scan-btn');
    setBtn(btn, true);
    const statusText = document.getElementById('tracker-status-text');
    const dot = document.querySelector('#tracker-status .dot');
    dot.className = 'dot dot-running';
    statusText.textContent = 'Escaneando Instagram... Espera, puede tardar varios minutos.';

    try {
        const res = await fetch('/run-bot', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            dot.className = 'dot dot-ok';
            statusText.textContent = `Escaneo completado. ${data.followers.length} seguidores totales.`;
            renderTrackerResults(data);
        } else {
            dot.className = 'dot dot-err';
            statusText.textContent = `Error: ${data.error}`;
        }
    } catch (e) {
        dot.className = 'dot dot-err';
        statusText.textContent = `Error de conexión: ${e.message}`;
    } finally {
        setBtn(btn, false);
    }
});

function renderTrackerResults(data) {
    const newF = data.changes?.new_followers || [];
    const unfol = data.changes?.unfollowers || [];
    const all = data.followers || [];
    lastNewFollowers = newF;

    document.getElementById('stat-new').textContent = newF.length;
    document.getElementById('stat-unfol').textContent = unfol.length;
    document.getElementById('stat-total').textContent = all.length;
    document.getElementById('tracker-stats').style.display = 'grid';
    document.getElementById('tracker-results').style.display = 'grid';

    renderUserList('new-list', newF, 'badge-new', '+');
    renderUserList('unfol-list', unfol, 'badge-unfol', '−');

    const allEl = document.getElementById('all-list');
    allEl.innerHTML = all.map((u, i) => `
        <div class="user-item" style="animation-delay:${i * 0.02}s">
            <span>@${u}</span>
        </div>`).join('');

    // Show "Send DMs" button if there are new followers
    const dmBtn = document.getElementById('dm-new-btn');
    dmBtn.style.display = newF.length > 0 ? 'inline-flex' : 'none';
}

// Quick "Send DMs to new followers" button from tracker tab
document.getElementById('dm-new-btn').addEventListener('click', () => {
    document.querySelector('[data-tab="dm"]').click();
    document.getElementById('dm-usernames').value = lastNewFollowers.join('\n');
});

// Reset followers memory
document.getElementById('reset-btn').addEventListener('click', async () => {
    if (!confirm('¿Borrar memoria de seguidores? El próximo scan tratará a todos como nuevos.')) return;
    const res = await fetch('/reset-followers', { method: 'POST' });
    const data = await res.json();
    alert(data.message);
});

// ── DM BOT ────────────────────────────────────────────────────
document.getElementById('load-new-btn').addEventListener('click', () => {
    if (lastNewFollowers.length > 0) {
        document.getElementById('dm-usernames').value = lastNewFollowers.join('\n');
    } else {
        alert('Primero ejecuta el tracker para detectar nuevos seguidores.');
    }
});

document.getElementById('dm-send-btn').addEventListener('click', async () => {
    const textarea = document.getElementById('dm-usernames');
    const usernames = textarea.value.split('\n').map(u => u.trim()).filter(Boolean);

    if (usernames.length === 0) {
        alert('Escribe al menos un usuario.');
        return;
    }

    const btn = document.getElementById('dm-send-btn');
    setBtn(btn, true);
    const statusBox = document.getElementById('dm-status');
    const statusText = document.getElementById('dm-status-text');
    statusBox.style.display = 'flex';
    statusBox.querySelector('.dot').className = 'dot dot-running';
    statusText.textContent = `Enviando DMs a ${usernames.length} usuario(s)... (puede tardar por los delays anti-spam)`;

    try {
        const res = await fetch('/send-dms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usernames })
        });
        const data = await res.json();

        if (data.success) {
            statusBox.querySelector('.dot').className = 'dot dot-ok';
            statusText.textContent = data.message;
            loadDmLog();
        } else {
            statusBox.querySelector('.dot').className = 'dot dot-err';
            statusText.textContent = `Error: ${data.error}`;
        }
    } catch (e) {
        statusBox.querySelector('.dot').className = 'dot dot-err';
        statusText.textContent = `Error de conexión: ${e.message}`;
    } finally {
        setBtn(btn, false);
    }
});

document.getElementById('refresh-log-btn').addEventListener('click', loadDmLog);

async function loadDmLog() {
    try {
        const res = await fetch('/dm-log');
        const data = await res.json();
        const list = document.getElementById('dm-log-list');
        if (!data.sent || data.sent.length === 0) {
            list.innerHTML = `<div class="empty-msg">Aún no se han enviado DMs</div>`;
        } else {
            list.innerHTML = data.sent.map((u, i) => `
                <div class="user-item" style="animation-delay:${i * 0.04}s">
                    <span class="badge badge-new">DM</span>
                    <span>@${u}</span>
                </div>`).join('');
        }
    } catch (e) {
        console.error('Error cargando log:', e);
    }
}

// Load DM log and followers on startup
loadDmLog();
