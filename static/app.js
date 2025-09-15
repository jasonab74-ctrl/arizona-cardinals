/* ===== Arizona Cardinals feed app =====
   Only responsibilities here:
   - Build the fixed sources dropdown (Cardinals-specific)
   - Load items.json (always cache-busted)
   - Render 50 most recent articles with Source · Date
   - Keep everything else exactly as-is visually
*/

/* 8–10 stable Cardinals sources for dropdown */
const SOURCES = [
  { key: 'All sources', label: 'All sources' },
  { key: 'Google News — Arizona Cardinals', label: 'Google News — Arizona Cardinals' },
  { key: 'Yahoo Sports — Cardinals',       label: 'Yahoo Sports — Cardinals' },
  { key: 'azcardinals.com',                 label: 'azcardinals.com' },
  { key: 'Arizona Sports',                  label: 'Arizona Sports' },
  { key: 'USA Today — Cards Wire',          label: 'USA Today — Cards Wire' },
  { key: 'Revenge of the Birds',            label: 'Revenge of the Birds' },
  { key: 'The Athletic',                    label: 'The Athletic' },
  { key: 'ProFootballTalk',                 label: 'ProFootballTalk' }
];

/* DOM */
const feedEl    = document.getElementById('feed');
const sel       = document.getElementById('sourceSelect');
const updatedEl = document.getElementById('updatedAt');

/* Build dropdown from fixed list (prevents “reverting”) */
(function buildDropdown(){
  sel.innerHTML = '';
  for (const s of SOURCES){
    const opt = document.createElement('option');
    opt.value = s.key;
    opt.textContent = s.label;
    sel.appendChild(opt);
  }
  sel.value = 'All sources';
})();

/* Always cache-bust items.json to avoid stale GH Pages cache */
async function loadItems(){
  const qs = `?v=${Date.now().toString().slice(0,10)}`;
  const res = await fetch(`items.json${qs}`, { cache:'no-store' });
  if (!res.ok) throw new Error(`Failed to load items.json (HTTP ${res.status})`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.items || []);
}

/* Robust date parsing */
function parseDate(any){
  if (!any) return null;
  if (any instanceof Date) return any;
  const s = String(any).replace(/\sat\s/i, ' ');  // “Sep 9, 2025 at 4:04 PM” -> “Sep 9, 2025 4:04 PM”
  const t = Date.parse(s);
  if (!Number.isNaN(t)) return new Date(t);
  try { return new Date(s); } catch { return null; }
}

/* Format for UI (ex: Sep 9, 2025, 4:04 PM) */
function fmt(dt){
  if (!dt) return '—';
  const d = dt.toLocaleDateString(undefined, { month:'short', day:'numeric', year:'numeric' });
  const t = dt.toLocaleTimeString(undefined, { hour:'numeric', minute:'2-digit' });
  return `${d}, ${t}`;
}

let ALL = [];

/* Render cards */
function render(){
  const pick = sel.value;
  let items = ALL;

  if (pick && pick !== 'All sources'){
    const key = pick.toLowerCase();
    items = items.filter(it => (it.source || '').toLowerCase() === key);
  }

  // Sort newest first by isoDate/date/pubDate
  items.sort((a,b) => {
    const da = parseDate(a.isoDate || a.date || a.pubDate);
    const db = parseDate(b.isoDate || b.date || b.pubDate);
    return (db?.getTime() || 0) - (da?.getTime() || 0);
  });

  // Limit to 50
  items = items.slice(0, 50);

  // Updated timestamp reflects newest article date (fallback to em dash)
  const newest = items.find(it => parseDate(it.isoDate || it.date || it.pubDate));
  updatedEl.textContent = newest ? fmt(parseDate(newest.isoDate || newest.date || newest.pubDate)) : '—';

  // Cards
  feedEl.innerHTML = '';
  for (const it of items){
    const d = parseDate(it.isoDate || it.date || it.pubDate);

    const card = document.createElement('article');
    card.className = 'card';

    const h3 = document.createElement('h3');
    h3.className = 'item-title';

    const a = document.createElement('a');
    a.href = it.link;
    a.target = '_blank';
    a.rel   = 'noopener';
    a.textContent = it.title || 'Untitled';

    h3.appendChild(a);

    const meta = document.createElement('div');
    meta.className = 'meta';

    const src = document.createElement('span');
    src.textContent = it.source || '—';

    const dot = document.createElement('span');
    dot.className = 'dot';

    const when = document.createElement('time');
    when.dateTime = d ? d.toISOString() : '';
    when.textContent = fmt(d);

    meta.append(src, dot, when);
    card.append(h3, meta);
    feedEl.appendChild(card);
  }
}

/* Init */
(async function(){
  try{
    ALL = await loadItems();
  }catch(err){
    console.error(err);
    ALL = [];
  }
  render();
})();

/* Events */
sel.addEventListener('change', render);