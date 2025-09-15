/* ===== Arizona Cardinals feed — stable dropdown + dates ===== */

/* 8–10 fixed NFL sources for the dropdown (labels only; items come from items.json) */
const SOURCES = [
  { key: 'All sources', label: 'All sources' },
  { key: 'Google News — Arizona Cardinals', label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals', label: 'Yahoo Sports — Cardinals' },
  { key: 'azcardinals.com', label: 'azcardinals.com' },
  { key: 'Revenge of the Birds', label: 'Revenge of the Birds' },
  { key: 'Arizona Sports', label: 'Arizona Sports' },
  { key: 'ESPN — Cardinals', label: 'ESPN — Cardinals' },
  { key: 'CBS Sports — Cardinals', label: 'CBS Sports — Cardinals' },
  { key: 'Cards Wire (USA Today)', label: 'Cards Wire (USA Today)' },
  { key: 'ProFootballTalk — Cardinals', label: 'ProFootballTalk — Cardinals' }
];

/* DOM handles */
const feedEl     = document.getElementById('feed');
const sel        = document.getElementById('sourceSelect');
const updatedEl  = document.getElementById('updatedAt');
const songBtn    = document.getElementById('songBtn');
const fightAudio = document.getElementById('fightAudio');

/* Build stable dropdown */
(function buildDropdown() {
  sel.innerHTML = '';
  for (const s of SOURCES) {
    const opt = document.createElement('option');
    opt.value = s.key;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = 'All sources';
})();

/* Load items.json (cache-busted so GH Pages doesn’t serve stale) */
async function loadItems() {
  const res = await fetch(`items.json?v=${Date.now().toString().slice(0,10)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.items || []);
}

/* Date helpers: accept isoDate / date / pubDate in a variety of shapes */
function parseDate(d) {
  if (!d) return null;
  const s = typeof d === 'string' ? d.replace(/\sat\s/i, ' ') : d;
  const t = Date.parse(s);
  if (!Number.isNaN(t)) return new Date(t);
  try { return new Date(s); } catch { return null; }
}
function fmtLocal(dt) {
  const date = dt.toLocaleDateString(undefined, { year:'numeric', month:'short', day:'numeric' });
  const time = dt.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  return `${date}, ${time}`;
}

/* Render */
let ALL = [];
function render() {
  const pick = sel.value;
  let items = ALL;

  if (pick && pick !== 'All sources') {
    const key = pick.toLowerCase();
    items = items.filter(it => (it.source || '').toLowerCase() === key);
  }

  // sort newest-first
  items.sort((a,b) => {
    const da = parseDate(a.isoDate || a.date || a.pubDate);
    const db = parseDate(b.isoDate || b.date || b.pubDate);
    return (db?.getTime() ?? 0) - (da?.getTime() ?? 0);
  });

  items = items.slice(0, 50);

  // updated banner = newest item date
  const newest = items.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? fmtLocal(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

  // cards
  feedEl.innerHTML = '';
  for (const it of items) {
    const card = document.createElement('article');
    card.className = 'card';

    const h3 = document.createElement('h3');
    h3.className = 'item-title';

    const a = document.createElement('a');
    a.href = it.link;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = it.title || 'Untitled';
    h3.appendChild(a);

    const meta = document.createElement('div');
    meta.className = 'meta';

    const src = document.createElement('span');
    src.textContent = it.source || '—';

    const dot = document.createElement('span');
    dot.textContent = ' • ';

    const when = document.createElement('time');
    const dt = parseDate(it.isoDate || it.date || it.pubDate);
    if (dt) when.dateTime = dt.toISOString();
    when.textContent = dt ? fmtLocal(dt) : '—';

    meta.append(src, dot, when);
    card.append(h3, meta);
    feedEl.appendChild(card);
  }
}

/* Init */
(async function () {
  try {
    ALL = await loadItems();
  } catch (err) {
    console.error('Failed to load items.json', err);
    ALL = [];
  }
  render();
})();
sel.addEventListener('change', render);

/* Song: play/pause toggle (iOS requires tap and silent off) */
songBtn?.addEventListener('click', async () => {
  try {
    if (fightAudio.paused) {
      await fightAudio.play();
      songBtn.setAttribute('aria-pressed', 'true');
      songBtn.querySelector('.pill__icon').textContent = '❚❚';
      songBtn.lastElementChild.textContent = 'Pause';
    } else {
      fightAudio.pause();
      fightAudio.currentTime = 0;
      songBtn.setAttribute('aria-pressed', 'false');
      songBtn.querySelector('.pill__icon').textContent = '►';
      songBtn.lastElementChild.textContent = 'Team Song';
    }
  } catch (e) {
    alert('Could not play audio. On iPhone, ensure Silent Mode is off and tap again. Also verify static/fight-song.mp3 exists.');
    console.warn(e);
  }
});