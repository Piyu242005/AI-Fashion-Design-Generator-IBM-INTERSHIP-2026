import React, { useEffect, useMemo, useState } from 'react';

const API = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=60&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=480&gsrsearch=';
const PAGE_SIZE = 60;
const MAX_IMAGES = 10000;

const QUERIES = {
  female: 'fashion model full body standing single person',
  male: 'male fashion model full body standing single person',
};

function looksVtonReady(item) {
  const title = item.name.toLowerCase();
  const good = /(full body|full-body|standing|fashion model|runway|model)/.test(title);
  const bad = /(group|collage|logo|poster|headshot|portrait|face|bust|close-up|closeup)/.test(title);
  return good && !bad;
}

export default function VTONModelCollection({ onSelect }) {
  const [open, setOpen] = useState(false);
  const [gender, setGender] = useState('female');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(0);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);

  const effectiveQuery = useMemo(() => {
    const base = QUERIES[gender];
    return query.trim() ? `${base} ${query.trim()}` : base;
  }, [gender, query]);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError('');
      try {
        const offset = page * PAGE_SIZE;
        if (offset >= MAX_IMAGES) return;
        const response = await fetch(API + encodeURIComponent(effectiveQuery) + `&gsroffset=${offset}`);
        if (!response.ok) throw new Error(`Wikimedia request failed (${response.status})`);
        const data = await response.json();
        if (data.error) throw new Error(data.error.info || 'Wikimedia API error');
        const pages = Object.values(data.query?.pages || {});
        const mapped = pages.map(p => {
          const info = p.imageinfo?.[0];
          return {
            id: p.pageid,
            name: p.title?.replace(/^File:/, '') || 'Model',
            url: info?.thumburl || info?.url,
            mime: info?.mime,
            width: info?.width || 0,
            height: info?.height || 0,
            source: `https://commons.wikimedia.org/wiki/${encodeURIComponent(p.title || '')}`,
          };
        }).filter(x => x.url && x.mime?.startsWith('image/'));
        if (!cancelled) setItems(mapped);
      } catch (e) {
        if (!cancelled) {
          setItems([]);
          setError(e.message || 'Unable to load models');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [open, page, effectiveQuery]);

  const useForVTON = async item => {
    setSelected(item.id);
    try {
      if (onSelect) await onSelect(item);
      setOpen(false);
    } finally {
      setSelected(null);
    }
  };

  const readyCount = items.filter(looksVtonReady).length;

  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className="px-3 py-2 rounded-xl border border-white/10 bg-white/5 text-xs text-neutral-300 hover:bg-white/10 hover:text-white">
        🧍 VTON Models
      </button>

      {open && (
        <div className="fixed inset-0 z-[20000] overflow-y-auto bg-black/95 p-4 sm:p-8">
          <section className="max-w-7xl mx-auto rounded-3xl border border-white/10 bg-neutral-950 p-5 sm:p-7">
            <header className="flex justify-between gap-4 items-start">
              <div>
                <p className="text-[10px] tracking-[.25em] text-neutral-500 font-bold">VIRTUAL TRY-ON · MODEL LIBRARY</p>
                <h2 className="text-2xl sm:text-4xl font-bold text-white mt-1">🧍 VTON Model Collection</h2>
                <p className="text-xs text-neutral-500 mt-2">Female and male model references optimized for full-body fashion try-on. Images load on demand.</p>
              </div>
              <button onClick={() => setOpen(false)} className="w-10 h-10 rounded-xl border border-white/10 bg-white/5 text-white text-xl">×</button>
            </header>

            <div className="flex flex-col sm:flex-row gap-2 mt-6">
              <div className="flex gap-2">
                <button onClick={() => { setGender('female'); setPage(0); }} className={`px-4 py-2 rounded-xl text-xs font-bold border ${gender === 'female' ? 'bg-pink-500 text-white border-pink-500' : 'bg-white/5 text-neutral-400 border-white/10'}`}>👩 Female</button>
                <button onClick={() => { setGender('male'); setPage(0); }} className={`px-4 py-2 rounded-xl text-xs font-bold border ${gender === 'male' ? 'bg-sky-500 text-white border-sky-500' : 'bg-white/5 text-neutral-400 border-white/10'}`}>👨 Male</button>
              </div>
              <input value={query} onChange={e => { setQuery(e.target.value); setPage(0); }} placeholder="Search pose, runway, outfit, model…" className="flex-1 px-4 py-2 rounded-xl border border-white/10 bg-white/5 text-white text-xs outline-none" />
            </div>

            <div className="flex gap-3 text-[10px] text-neutral-500 mt-3">
              <span>VTON-ready heuristic: {readyCount}/{items.length}</span>
              <span>•</span><span>Page {page + 1}</span>
            </div>

            {loading && <div className="py-12 text-center text-xs text-neutral-500">Loading VTON model references…</div>}
            {error && <div className="mt-4 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-xs text-red-300">{error}</div>}

            {!loading && !error && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-6 gap-3 mt-5">
                {items.map(item => {
                  const ready = looksVtonReady(item);
                  return (
                    <article key={item.id} className="overflow-hidden rounded-2xl border border-white/8 bg-white/[.03] group">
                      <a href={item.source} target="_blank" rel="noopener noreferrer">
                        <img src={item.url} loading="lazy" alt={item.name} className="w-full aspect-[3/4] object-cover object-top group-hover:scale-[1.03] transition-transform" />
                      </a>
                      <div className="p-2">
                        <p className="text-[10px] text-white truncate" title={item.name}>{item.name}</p>
                        <div className="flex items-center justify-between mt-1">
                          <span className={`text-[8px] font-bold ${ready ? 'text-emerald-400' : 'text-neutral-600'}`}>{ready ? '● VTON READY' : '○ REVIEW'}</span>
                          <span className="text-[8px] text-neutral-600">{item.width}×{item.height}</span>
                        </div>
                        <button disabled={!ready || selected === item.id} onClick={() => useForVTON(item)} className="w-full mt-2 py-1.5 rounded-lg bg-white text-black text-[9px] font-extrabold disabled:opacity-30">
                          {selected === item.id ? 'Selecting…' : '✨ Use for VTON'}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {!loading && !error && !items.length && <div className="py-12 text-center text-xs text-neutral-600">No model images found. Try another search.</div>}

            <div className="flex justify-center items-center gap-4 mt-6">
              <button disabled={page === 0} onClick={() => setPage(p => Math.max(0, p - 1))} className="px-4 py-2 rounded-xl border border-white/10 bg-white/5 text-xs text-white disabled:opacity-30">← Previous</button>
              <span className="text-xs text-neutral-500">60 per page · up to 10,000 catalog items</span>
              <button disabled={items.length < PAGE_SIZE || (page + 1) * PAGE_SIZE >= MAX_IMAGES} onClick={() => setPage(p => p + 1)} className="px-4 py-2 rounded-xl border border-white/10 bg-white/5 text-xs text-white disabled:opacity-30">Next →</button>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
