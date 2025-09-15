/* ---------- Arizona Cardinals feed UI (dates + fixed sources) ---------- */

/* 8–10 stable Cardinals sources for the dropdown (never “roll back”) */
const SOURCES = [
  { key: 'All sources',                    label: 'All sources' },
  { key: 'Google News — Arizona Cardinals',label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals',       label: 'Yahoo Sports — Cardinals' },
  { key: 'ESPN — Cardinals',               label: 'ESPN — Cardinals' },
  { key: 'azcardinals.com',                label: 'azcardinals.com' },
  { key: 'Arizona Sports',                 label: 'Arizona Sports' },
  { key: 'USA Today — Cards Wire',         label: 'USA Today — Cards Wire' },
  { key: 'Revenge of the Birds',           label: 'Revenge of the Birds' },
  { key: 'The Athletic',                   label: 'The Athletic' },
  { key: 'ProFootballTalk',                label: 'ProFootballTalk' },
  { key: 'AZ Central',                     label: 'AZ Central' },
];

/* DOM */
const feedEl    = document.getElementById('feed');
const sel       = document.getElementById('sourceSelect');
const updatedEl = document.getElementById('updatedAt');

/* Build the dropdown once from our fixed list */
(function buildDropdown () {
  sel.innerHTML = '';
  for (const s of SOURCES) {
    const opt = document.createElement('option');
    opt.value = s.key;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = 'All sources';
})();

/* Load items.json (cache-bust avoids GH Pages caching old JSON) */
async function loadItems () {
  const res = await fetch(`items.json?cb=${Date.now().toString().slice(0,10)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`items.json HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.items || []);
}

/* Robust date parsing for mixed feeds */
function parseDate (raw) {
  if (!raw) return null;
  const s = typeof raw === 'string' ? raw.replace(/\sat\s/i, ' ') : raw;
  const t = Date.parse(s);
  if (!Number.isNaN(t)) return new Date(t);
  try { return new Date(s); } catch { return null; }
}

/* Date -> readable local string (e.g., "Sep 9, 2025, 4:04 PM") */
function formatLocal (d) {
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit'
  });
}

/* Render cards (50 newest) */
let ALL = [];
function render () {
  const pick = sel.value;
  let items = ALL;

  if (pick && pick !== 'All sources') {
    items = items.filter(it => (it.source || '').toLowerCase() === pick.toLowerCase());
  }

  items.sort((a, b) => {
    const da = parseDate(a.isoDate || a.date || a.pubDate);
    const db = parseDate(b.isoDate || b.date || b.pubDate);
    return (db?.getTime() ?? 0) - (da?.getTime() ?? 0);
  });

  items = items.slice(0, 50);

  const newest = items.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? formatLocal(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

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
    dot.className = 'dot';
    dot.textContent = '•';
    const when = document.createElement('time');
    const dt = parseDate(it.isoDate || it.date || it.pubDate);
    when.dateTime = dt ? dt.toISOString() : '';
    when.textContent = dt ? formatLocal(dt) : '—';

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

/* Interactions */
sel.addEventListener('change', render);