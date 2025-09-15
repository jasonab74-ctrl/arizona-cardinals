/* ===========================================================
   Arizona Cardinals feed app (stable dropdown + dates)
   =========================================================== */

/* ----- 8–12 fixed Cardinals sources for a stable dropdown ----- */
const SOURCES = [
  { key: 'All sources', label: 'All sources' },
  { key: 'Google News — Arizona Cardinals', label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals',      label: 'Yahoo Sports — Cardinals' },
  { key: 'ESPN — Cardinals',              label: 'ESPN — Cardinals' },
  { key: 'azcardinals.com',               label: 'azcardinals.com' },
  { key: 'Arizona Sports',                label: 'Arizona Sports' },
  { key: 'USA Today — Cards Wire',        label: 'USA Today — Cards Wire' },
  { key: 'Revenge of the Birds',          label: 'Revenge of the Birds' },
  { key: 'The Athletic',                  label: 'The Athletic' },
  { key: 'ProFootballTalk',               label: 'ProFootballTalk' }
];

/* DOM */
const feedEl    = document.getElementById('feed');
const sel       = document.getElementById('sourceSelect');
const updatedEl = document.getElementById('updatedAt');

/* Build dropdown from the fixed list (prevents “roll back”) */
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

/* Load items.json (cache-bust to avoid old GH Pages cache) */
async function loadItems(){
  const cacheBust = `?v=${Date.now().toString().slice(0,10)}`;
  const res = await fetch(`items.json${cacheBust}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const items = await res.json();
  return Array.isArray(items) ? items : (items.items || []);
}

/* Robust date parsing */
function parseDate(d){
  if (!d) return null;
  const cleaned = typeof d === 'string' ? d.replace(/\sat\s/i, ' ') : d;
  const t = Date.parse(cleaned);
  if (!Number.isNaN(t)) return new Date(t);
  try { return new Date(cleaned); } catch { return null; }
}

/* Friendly date like “Sep 7, 2025, 4:36 PM” */
function formatLocal(d){
  const dateStr = d.toLocaleDateString(undefined, { year:'numeric', month:'short', day:'numeric' });
  const timeStr = d.toLocaleTimeString(undefined, { hour:'numeric', minute:'2-digit' });
  return `${dateStr}, ${timeStr}`;
}

/* Render feed (50 newest) */
let allItems = [];
function normalizeSource(s=''){
  // Allow contains/variants matching for the dropdown
  const lc = s.toLowerCase();
  if (lc.includes('google news'))         return 'Google News — Arizona Cardinals';
  if (lc.includes('yahoo') && lc.includes('cardinals')) return 'Yahoo Sports — Cardinals';
  if (lc.includes('espn'))                return 'ESPN — Cardinals';
  if (lc.includes('azcardinals.com'))     return 'azcardinals.com';
  if (lc.includes('arizonasports'))       return 'Arizona Sports';
  if (lc.includes('cards wire') || lc.includes('usatoday')) return 'USA Today — Cards Wire';
  if (lc.includes('revenge of the birds')) return 'Revenge of the Birds';
  if (lc.includes('the athletic'))        return 'The Athletic';
  if (lc.includes('profootballtalk'))     return 'ProFootballTalk';
  return s;
}

function render(){
  const pick = sel.value;
  let items = allItems.map(it => ({ ...it, _srcNorm: normalizeSource(it.source || '') }));

  if (pick && pick !== 'All sources') {
    items = items.filter(it => it._srcNorm.toLowerCase() === pick.toLowerCase());
  }

  items.sort((a,b) => {
    const da = parseDate(a.isoDate || a.date || a.pubDate) ?? 0;
    const db = parseDate(b.isoDate || b.date || b.pubDate) ?? 0;
    return db - da;
  });

  items = items.slice(0, 50);

  const newest = items.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? formatLocal(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

  feedEl.innerHTML = '';
  for (const it of items) {
    const dt = parseDate(it.isoDate || it.date || it.pubDate);

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
    src.textContent = normalizeSource(it.source || '—');
    const dot = document.createElement('span');
    dot.textContent = '•';
    const when = document.createElement('time');
    when.dateTime = dt ? dt.toISOString() : '';
    when.textContent = dt ? formatLocal(dt) : '—';

    meta.append(src, dot, when);
    card.append(h3, meta);
    feedEl.appendChild(card);
  }
}

/* Init */
(async function(){
  try {
    allItems = await loadItems();
  } catch (e) {
    console.error('Failed to load items.json', e);
    allItems = [];
  }
  render();
})();

sel.addEventListener('change', render);