import React, { useEffect, useState } from 'react';

const API = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=60&gsrsearch=';
const PAGE_SIZE = 60;
const MAX_IMAGES = 10000;

export default function MissUniverseCollection() {
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [query, setQuery] = useState('Miss Universe');
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selecting, setSelecting] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (!open) return;
      setLoading(true);
      try {
        const offset = page * PAGE_SIZE;
        if (offset >= MAX_IMAGES) return;
        const url = API + encodeURIComponent(query || 'Miss Universe') + `&gsroffset=${offset}`;
        const response = await fetch(url);
        const data = await response.json();
        const pages = Object.values(data.query?.pages || {});
        const mapped = pages.map(p => {
          const info = p.imageinfo?.[0];
          return {
            id: p.pageid,
            name: p.title?.replace(/^File:/, ''),
            url: info?.thumburl || info?.url,
            source: `https://commons.wikimedia.org/wiki/${encodeURIComponent(p.title || '')}`,
          };
        }).filter(x => x.url);
        if (!cancelled) {
          setItems(mapped);
          setTotal(Math.min(Number(data.query?.searchinfo?.totalhits || 0), MAX_IMAGES));
        }
      } catch {
        if (!cancelled) setItems([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [open, page, query]);

  useEffect(() => {
    if (!open) return;
    const old = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = old; };
  }, [open]);

  useEffect(() => {
    const timer = setInterval(() => {
      const buttons = [...document.querySelectorAll('button')];
      const target = buttons.find(b => b.textContent?.includes('Model Photos'));
      if (!target || document.getElementById('mu-collection-launcher')) return;
      const button = document.createElement('button');
      button.id = 'mu-collection-launcher';
      button.textContent = '👑 Miss Universe (10K)';
      button.className = target.className;
      button.style.marginLeft = '4px';
      button.onclick = () => setOpen(true);
      target.parentElement?.appendChild(button);
    }, 500);
    return () => clearInterval(timer);
  }, []);

  const useModelForVTON = async (item) => {
    if (!item?.url || selecting) return;
    setSelecting(item.id);
    try {
      const response = await fetch(item.url);
      if (!response.ok) throw new Error(`Image request failed (${response.status})`);
      const blob = await response.blob();
      const ext = blob.type?.split('/')[1] || 'jpeg';
      const file = new File([blob], `miss-universe-${item.id}.${ext}`, { type: blob.type || 'image/jpeg' });

      // The existing VTON UI owns the real person File state. Populate its
      // hidden file input so the normal upload/change handler remains the
      // single source of truth and IDM-VTON receives a real File object.
      const input = [...document.querySelectorAll('input[type="file"]')]
        .find(el => el.accept?.includes('image'));
      if (!input) throw new Error('VTON image input is not available. Open Try-On and retry.');

      const transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));

      // Select the existing Try-On tab without changing the original navbar.
      const tryOnButton = [...document.querySelectorAll('button')]
        .find(b => b.textContent?.trim() === 'Try-On');
      if (tryOnButton) tryOnButton.click();

      setOpen(false);
    } catch (error) {
      window.alert(`Could not load this model for VTON: ${error.message}`);
    } finally {
      setSelecting(null);
    }
  };

  if (!open) return null;

  const maxPage = Math.max(0, Math.ceil(total / PAGE_SIZE) - 1);
  const shown = Math.min(total || MAX_IMAGES, MAX_IMAGES);

  return (
    <div style={S.overlay}>
      <section style={S.panel}>
        <header style={S.header}>
          <div>
            <div style={S.eyebrow}>COLLECTION · PAGEANT ARCHIVE</div>
            <h1 style={S.title}>👑 Miss Universe Image Collection</h1>
            <p style={S.sub}>Up to 10,000+ searchable Miss Universe images. Select any suitable image and send it directly to Virtual Try-On.</p>
          </div>
          <button style={S.close} onClick={() => setOpen(false)}>×</button>
        </header>

        <div style={S.toolbar}>
          <input
            value={query}
            onChange={e => { setQuery(e.target.value); setPage(0); }}
            placeholder="Search Miss Universe, year, contestant, country…"
            style={S.input}
          />
          <span style={S.count}>{shown.toLocaleString()} max catalog</span>
        </div>

        {loading && <div style={S.notice}>Loading images from Wikimedia Commons…</div>}

        <div style={S.grid}>
          {items.map(item => (
            <div key={item.id} style={S.card}>
              <a href={item.source} target="_blank" rel="noopener noreferrer" style={{display:'block',textDecoration:'none',color:'#fff'}}>
                <img src={item.url} loading="lazy" alt={item.name} style={S.img} />
              </a>
              <div style={S.meta}>
                <span title={item.name}>{item.name}</span>
                <small>Wikimedia Commons ↗</small>
                <button
                  onClick={() => useModelForVTON(item)}
                  disabled={selecting === item.id}
                  style={S.vtonBtn}
                >
                  {selecting === item.id ? 'Loading…' : '✨ Use for VTON'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {!loading && !items.length && <div style={S.empty}>No images found. Try another search.</div>}

        <div style={S.pagination}>
          <button disabled={page === 0} onClick={() => setPage(p => Math.max(0, p - 1))} style={S.pageBtn}>← Previous</button>
          <span>Page {page + 1} · {items.length} images</span>
          <button disabled={items.length < PAGE_SIZE || page >= maxPage || (page + 1) * PAGE_SIZE >= MAX_IMAGES} onClick={() => setPage(p => p + 1)} style={S.pageBtn}>Next →</button>
        </div>

        <p style={S.footer}>
          Images load on demand and are not copied into the repository. Wikimedia Commons provides source and licensing information for each result. The 10,000 limit is an application catalog cap. VTON works by passing the selected image through the existing person-image upload flow to IDM-VTON.
        </p>
      </section>
    </div>
  );
}

const S = {
  overlay:{position:'fixed',inset:0,zIndex:20000,background:'#050505f7',padding:'24px',overflowY:'auto'},
  panel:{maxWidth:1400,margin:'0 auto',background:'#0d0d0d',color:'#fff',border:'1px solid #292929',borderRadius:24,padding:24,boxShadow:'0 30px 100px #000'},
  header:{display:'flex',justifyContent:'space-between',gap:20,alignItems:'flex-start'},
  eyebrow:{fontSize:10,letterSpacing:3,color:'#888',fontWeight:900},
  title:{fontSize:'clamp(25px,4vw,48px)',margin:'6px 0'},
  sub:{color:'#888',margin:0,maxWidth:800},
  close:{width:44,height:44,borderRadius:12,border:'1px solid #333',background:'#171717',color:'#fff',fontSize:28,cursor:'pointer'},
  toolbar:{display:'flex',gap:12,alignItems:'center',margin:'22px 0'},
  input:{flex:1,padding:13,borderRadius:12,border:'1px solid #333',background:'#171717',color:'#fff',boxSizing:'border-box'},
  count:{color:'#777',whiteSpace:'nowrap',fontSize:12},
  notice:{padding:12,borderRadius:12,background:'#151515',color:'#999',marginBottom:14},
  grid:{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(160px,1fr))',gap:12},
  card:{background:'#151515',border:'1px solid #292929',borderRadius:14,overflow:'hidden',color:'#fff'},
  img:{width:'100%',height:230,objectFit:'cover',display:'block'},
  meta:{padding:9,display:'grid',gap:5},
  vtonBtn:{padding:'9px 10px',border:0,borderRadius:9,background:'#fff',color:'#000',fontWeight:800,cursor:'pointer'},
  empty:{padding:50,textAlign:'center',color:'#666'},
  pagination:{display:'flex',justifyContent:'center',alignItems:'center',gap:18,marginTop:22,color:'#888',fontSize:12},
  pageBtn:{padding:'10px 14px',border:'1px solid #333',background:'#171717',color:'#fff',borderRadius:10,cursor:'pointer'},
  footer:{color:'#666',fontSize:11,lineHeight:1.5,marginTop:18}
};
