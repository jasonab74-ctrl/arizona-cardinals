/* ---------- Cardinals sources (fixed, stable dropdown) ---------- */
const SOURCES = [
  { key: 'All sources', label: 'All sources' },

  { key: 'Google News — Arizona Cardinals', label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals',        label: 'Yahoo Sports — Cardinals' },
  { key: 'ESPN — Cardinals',                label: 'ESPN — Cardinals' },

  { key: 'azcardinals.com',                 label: 'azcardinals.com' },
  { key: 'Arizona Sports',                  label: 'Arizona Sports' },
  { key: 'USA Today — Cards Wire',          label: 'USA Today — Cards Wire' },
  { key: 'Revenge of the Birds',            label: 'Revenge of the Birds' },
  { key: 'The Athletic',                    label: 'The Athletic' },
  { key: 'ProFootballTalk',                 label: 'ProFootballTalk' },
];

/* ---------- DOM ---------- */
const feedEl    = document.getElementById('feed');
const sel       = document.getElementById('sourceSelect');
const updatedEl = document.getElementById('updatedAt');

/* ---------- Build dropdown (won’t “disappear”) ---------- */
(function buildDropdown() {
  sel.innerHTML = '';
  for (const s of SOURCES) {
    const o = document.createElement('option');
    o.value = s.key;
    o.textContent = s.label;
    sel.appendChild(o);
  }
  sel.value = 'All sources';
})();

/* ---------- Load items.json with cache-bust to avoid GH cache ---------- */
async function loadItems() {
  const qs = `?v=${Date.now().toString().slice(0,10)}`;
  const res = await fetch(`items.json${qs}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.items || []);
}

/* ---------- Robust date parsing (kills the 1970 bug) ---------- */
function parseDate(raw) {
  if (!raw) return null;

  if (raw instanceof Date) return raw;

  let s = String(raw).trim();

  // Common "Sep 9, 2025, 4:31 PM" / "Sep 9, 2025 at 4:31 PM"
  s = s.replace(/\bat\b/i, ' ').replace(/\s{2,}/g, ' ').trim();

  // Try native Date first
  const t = Date.parse(s);
  if (!Number.isNaN(t)) return new Date(t);

  // Fallbacks: RFC822-ish with commas missing
  // e.g., "Tue, 09 Sep 2025 16:31:00 GMT" or "Sep 9 2025 16:31"
  const tryFormats = [
    s.replace(/(\d{1,2})(st|nd|rd|th)/i, '$1'), // strip ordinal
  ];
  for (const cand of tryFormats) {
    const ts = Date.parse(cand);
    if (!Number.isNaN(ts)) return new Date(ts);
  }
  return null; // unknown
}

function fmtDate(d) {
  // Example: Sep 2, 2025, 7:56 AM
  const optsD = { year:'numeric', month:'short', day:'numeric' };
  const optsT = { hour:'numeric', minute:'2-digit' };
  return `${d.toLocaleDateString(undefined, optsD)}, ${d.toLocaleTimeString(undefined, optsT)}`;
}

/* ---------- Render ---------- */
let ALL = [];

function render() {
  const pick = sel.value;
  let items = ALL.slice();

  if (pick && pick !== 'All sources') {
    const key = pick.toLowerCase();
    items = items.filter(it => (it.source || '').toLowerCase() === key);
  }

  // Sort newest first using isoDate, date, or pubDate
  items.sort((a,b) => {
    const db = parseDate(b.isoDate || b.date || b.pubDate);
    const da = parseDate(a.isoDate || a.date || a.pubDate);
    return (db ? db.getTime() : 0) - (da ? da.getTime() : 0);
  });

  items = items.slice(0, 50);

  // Updated stamp = newest date or —
  const newest = items.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? fmtDate(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

  // Draw cards
  feedEl.innerHTML = '';
  for (const it of items) {
    const when = parseDate(it.isoDate || it.date || it.pubDate);

    const card = document.createElement('article');
    card.className = 'card';

    const h3 = document.createElement('h3');
    h3.className = 'item-title';
    const a = document.createElement('a');
    a.href = it.link; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = it.title || 'Untitled';
    h3.appendChild(a);

    const meta = document.createElement('div');
    meta.className = 'meta';
    const src = document.createElement('span');
    src.textContent = it.source || '—';
    const dot = document.createElement('span'); dot.className = 'dot'; dot.textContent = '•';
    const time = document.createElement('time');
    time.dateTime = when ? when.toISOString() : '';
    time.textContent = when ? fmtDate(when) : '—';

    meta.append(src, dot, time);
    card.append(h3, meta);
    feedEl.appendChild(card);
  }
}

/* ---------- Init ---------- */
(async function init(){
  try {
    ALL = await loadItems();
  } catch (e) {
    console.warn('Failed to load items.json', e);
    ALL = [];
  }
  render();
})();

/* ---------- Events ---------- */
sel.addEventListener('change', render);