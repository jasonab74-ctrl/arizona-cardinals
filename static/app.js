/* --------- Fixed Cardinals sources for the dropdown ---------- */
const SOURCES = [
  { key: 'All sources', label: 'All sources' },
  { key: 'Google News — Arizona Cardinals', label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals',       label: 'Yahoo Sports — Cardinals' },
  { key: 'azcardinals.com',                label: 'azcardinals.com' },
  { key: 'ESPN — Cardinals',               label: 'ESPN — Cardinals' },
  { key: 'Arizona Sports',                 label: 'Arizona Sports' },
  { key: 'Cards Wire',                     label: 'Cards Wire' },
  { key: 'Revenge of the Birds',           label: 'Revenge of the Birds' },
  { key: 'The Athletic — Cardinals',       label: 'The Athletic — Cardinals' },
  { key: 'ProFootballTalk — Cardinals',    label: 'ProFootballTalk — Cardinals' }
];

/* --------- DOM --------- */
const feedEl    = document.getElementById('feed');
const sel       = document.getElementById('sourceSelect');
const updatedEl = document.getElementById('updatedAt');

/* Build dropdown (stable; won’t “revert”) */
(function buildDropdown(){
  sel.innerHTML = '';
  for (const s of SOURCES) {
    const opt = document.createElement('option');
    opt.value = s.key;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = 'All sources';
})();

/* Load items.json with cache-bust to avoid GH Pages cache */
async function loadItems(){
  const res = await fetch(`items.json?ts=${Date.now().toString().slice(0,10)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const items = await res.json();
  return Array.isArray(items) ? items : (items.items || []);
}

/* Robust date parsing (handles ISO, RFC822, “Sep 9, 2025 7:01 AM”, etc.) */
function parseDate(raw){
  if (!raw) return null;
  const s = String(raw).replace(/\sat\s/i, ' '); // normalize: remove " at "
  const t = Date.parse(s);
  if (!Number.isNaN(t)) return new Date(t);
  try { return new Date(s); } catch { return null; }
}

/* Date formatter (local, concise) */
function fmt(d){
  return d.toLocaleString(undefined,{
    year:'numeric', month:'short', day:'numeric',
    hour:'numeric', minute:'2-digit'
  });
}

/* Render feed */
let ALL = [];
function render(){
  const pick = sel.value;
  let list = ALL;

  if (pick && pick !== 'All sources') {
    list = list.filter(it => (it.source || '').toLowerCase() === pick.toLowerCase());
  }

  // newest first
  list.sort((a,b) => {
    const da = parseDate(a.isoDate || a.date || a.pubDate);
    const db = parseDate(b.isoDate || b.date || b.pubDate);
    return (db?.getTime() ?? 0) - (da?.getTime() ?? 0);
  });

  list = list.slice(0,50);

  const newest = list.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? fmt(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

  feedEl.innerHTML = '';
  for (const it of list) {
    const card = document.createElement('article');
    card.className = 'card';

    const h3 = document.createElement('h3');
    h3.className = 'item-title';
    const a = document.createElement('a');
    a.href = it.link; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = it.title || 'Untitled';
    h3.appendChild(a);

    const meta = document.createElement('div'); meta.className = 'meta';
    const src  = document.createElement('span'); src.textContent = it.source || '—';
    const dot  = document.createElement('span'); dot.textContent = '•';
    const when = document.createElement('time');
    const d    = parseDate(it.isoDate || it.date || it.pubDate);
    when.dateTime = d ? d.toISOString() : '';
    when.textContent = d ? fmt(d) : '—';

    meta.append(src, dot, when);
    card.append(h3, meta);
    feedEl.appendChild(card);
  }
}

/* Init */
(async function(){
  try {
    ALL = await loadItems();
  } catch (err) {
    console.error('items.json load failed:', err);
    ALL = [];
  }
  render();
})();

sel.addEventListener('change', render);