import React, { useEffect, useMemo, useState } from 'react';

const API = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=60&gsrsearch=';

const WINNER_LOOKS = [
  ['1952','Armi Kuusela','Finland'],['1953','Christiane Martel','France'],['1954','Miriam Stevenson','United States'],
  ['1955','Hillevi Rombin','Sweden'],['1956','Carol Morris','United States'],['1957','Gladys Zender','Peru'],
  ['1958','Luz Marina Zuluaga','Colombia'],['1959','Akiko Kojima','Japan'],['1960','Linda Bement','United States'],
  ['1961','Marlene Schmidt','Germany'],['1962','Norma Nolan','Argentina'],['1963','Iêda Maria Vargas','Brazil'],
  ['1964','Corinna Tsopei','Greece'],['1965','Apasra Hongsakula','Thailand'],['1966','Margareta Arvidsson','Sweden'],
  ['1967','Sylvia Hitchcock','United States'],['1968','Martha Vasconcellos','Brazil'],['1969','Gloria Diaz','Philippines'],
  ['1970','Marisol Malaret','Puerto Rico'],['1971','Georgina Rizk','Lebanon'],['1972','Kerry Anne Wells','Australia'],
  ['1973','Margarita Moran','Philippines'],['1974','Amparo Muñoz','Spain'],['1975','Anne Marie Pohtamo','Finland'],
  ['1976','Rina Messinger','Israel'],['1977','Janelle Commissiong','Trinidad and Tobago'],['1978','Margaret Gardiner','South Africa'],
  ['1979','Maritza Sayalero','Venezuela'],['1980','Shawn Weatherly','United States'],['1981','Irene Sáez','Venezuela'],
  ['1982','Karen Dianne Baldwin','Canada'],['1983','Lorraine Downes','New Zealand'],['1984','Yvonne Ryding','Sweden'],
  ['1985','Deborah Carthy-Deu','Puerto Rico'],['1986','Bárbara Palacios','Venezuela'],['1987','Cecilia Bolocco','Chile'],
  ['1988','Porntip Nakhirunkanok','Thailand'],['1989','Angela Visser','Netherlands'],['1990','Mona Grudt','Norway'],
  ['1991','Lupita Jones','Mexico'],['1992','Michelle McLean','Namibia'],['1993','Dayanara Torres','Puerto Rico'],
  ['1994','Sushmita Sen','India'],['1995','Chelsi Smith','United States'],['1996','Alicia Machado','Venezuela'],
  ['1997','Brook Lee','United States'],['1998','Wendy Fitzwilliam','Trinidad and Tobago'],['1999','Mpule Kwelagobe','Botswana'],
  ['2000','Lara Dutta','India'],['2001','Denise Quiñones','Puerto Rico'],['2002','Justine Pasek','Panama'],
  ['2002','Oxana Fedorova','Russia'],['2003','Amelia Vega','Dominican Republic'],['2004','Jennifer Hawkins','Australia'],
  ['2005','Natalie Glebova','Canada'],['2006','Zuleyka Rivera','Puerto Rico'],['2007','Riyo Mori','Japan'],
  ['2008','Dayana Mendoza','Venezuela'],['2009','Stefanía Fernández','Venezuela'],['2010','Ximena Navarrete','Mexico'],
  ['2011','Leila Lopes','Angola'],['2012','Olivia Culpo','United States'],['2013','Gabriela Isler','Venezuela'],
  ['2014','Paulina Vega','Colombia'],['2015','Pia Wurtzbach','Philippines'],['2016','Iris Mittenaere','France'],
  ['2017','Demi-Leigh Nel-Peters','South Africa'],['2018','Catriona Gray','Philippines'],['2019','Zozibini Tunzi','South Africa'],
  ['2020','Andrea Meza','Mexico'],['2021','Harnaaz Sandhu','India'],['2022',"R'Bonney Gabriel",'United States'],
  ['2023','Sheynnis Palacios','Nicaragua'],['2024','Victoria Kjær Theilvig','Denmark'],['2025','Fátima Bosch','Mexico']
];

function makeLook(name, year, country) {
  return `Miss Universe-inspired ${year} pageant look inspired by ${name} of ${country}, couture evening gown, elegant silhouette, refined stage styling, crown-ready glamour, full-body fashion editorial, realistic studio photography`;
}

export default function MissUniverseNav() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState('looks');
  const [q, setQ] = useState('fashion model');
  const [page, setPage] = useState(0);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

  const winners = useMemo(() => {
    const s = q.toLowerCase();
    return WINNER_LOOKS.filter(x => `${x[0]} ${x[1]} ${x[2]}`.toLowerCase().includes(s));
  }, [q]);

  useEffect(() => {
    if (!open || tab !== 'models') return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const url = API + encodeURIComponent(q || 'fashion model') + `&gsroffset=${page * 60}`;
        const r = await fetch(url);
        const d = await r.json();
        const pages = Object.values(d.query?.pages || {});
        const mapped = pages.map(p => ({
          id: p.pageid,
          name: p.title?.replace(/^File:/, ''),
          url: p.imageinfo?.[0]?.thumburl || p.imageinfo?.[0]?.url,
          source: `https://commons.wikimedia.org/wiki/${encodeURIComponent(p.title || '')}`
        })).filter(x => x.url);
        if (!cancelled) { setItems(mapped); setTotal(Number(d.query?.searchinfo?.totalhits || 0)); }
      } catch {
        if (!cancelled) { setItems([]); setTotal(0); }
      } finally { if (!cancelled) setLoading(false); }
    })();
    return () => { cancelled = true; };
  }, [open, tab, q, page]);

  const selectModel = model => {
    setSelected(model);
    localStorage.setItem('vton_selected_model', JSON.stringify(model));
    window.dispatchEvent(new CustomEvent('vton-model-selected', { detail: model }));
  };

  return <>
    <nav style={S.nav}>
      <div style={S.brand}>✦ AI FASHION STUDIO</div>
      <div style={S.links}>
        <button style={S.link} onClick={() => { setTab('looks'); setOpen(true); }}>👑 Miss Universe Looks</button>
        <button style={S.link} onClick={() => { setTab('models'); setOpen(true); }}>🧍 Model Library <b>10K+</b></button>
      </div>
    </nav>

    {open && <div style={S.overlay}>
      <section style={S.panel}>
        <header style={S.header}>
          <div><small style={S.eyebrow}>AI FASHION STUDIO · VTON</small><h1 style={S.title}>Miss Universe Looks & Model Library</h1><p style={S.sub}>Choose a pageant-inspired look or a full-body model source for virtual try-on.</p></div>
          <button style={S.close} onClick={() => setOpen(false)}>×</button>
        </header>
        <div style={S.tabs}>
          <button style={tab==='looks'?S.active:S.tab} onClick={() => setTab('looks')}>👑 Miss Universe Looks</button>
          <button style={tab==='models'?S.active:S.tab} onClick={() => setTab('models')}>🧍 10,000+ Model Collection</button>
        </div>

        {tab === 'looks' ? <>
          <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search winner or country…" style={S.input}/>
          <div style={S.grid}>{winners.map(([year,name,country]) => <article key={`${year}-${name}`} style={S.card}>
            <div style={S.crown}>👑</div><strong>{name}</strong><span>{country}</span><small>{year}</small>
            <button style={S.action} onClick={() => { localStorage.setItem('miss_universe_look_prompt', makeLook(name,year,country)); setSelected({name,year,country,prompt:makeLook(name,year,country)}); }}>Try this look →</button>
          </article>)}</div>
        </> : <>
          <div style={S.searchRow}><input value={q} onChange={e=>{setQ(e.target.value);setPage(0)}} placeholder="Search Wikimedia model photos…" style={S.input}/><span style={S.count}>{total ? `${total.toLocaleString()}+ results indexed` : 'Loading collection…'}</span></div>
          {loading && <div style={S.notice}>Loading model photographs from Wikimedia Commons…</div>}
          <div style={S.modelGrid}>{items.map(m => <article key={m.id} style={S.modelCard}><img src={m.url} loading="lazy" alt={m.name} style={S.img}/><div style={S.meta}><strong title={m.name}>{m.name}</strong><button style={S.action} onClick={()=>selectModel(m)}>Use for VTON</button></div></article>)}</div>
          <div style={S.pagination}><button disabled={page===0} onClick={()=>setPage(p=>Math.max(0,p-1))} style={S.pageBtn}>← Previous</button><span>Page {page+1}</span><button disabled={items.length<60} onClick={()=>setPage(p=>p+1)} style={S.pageBtn}>Next →</button></div>
          <p style={S.footer}>The 10K+ figure is an on-demand searchable catalog backed by Wikimedia Commons search, not 10,000 files stored in your Git repository. Only selected images are loaded into the browser. Check the individual Wikimedia file license before reuse.</p>
        </>}

        {selected && <div style={S.selected}><b>Selected:</b> {selected.name || selected.prompt}<span>Ready for the VTON workflow.</span></div>}
      </section>
    </div>}
  </>;
}

const S={
 nav:{position:'fixed',top:0,left:0,right:0,zIndex:9990,height:58,display:'flex',alignItems:'center',justifyContent:'space-between',padding:'0 20px',background:'#080808eF',backdropFilter:'blur(16px)',borderBottom:'1px solid #252525',color:'#fff'},
 brand:{fontSize:12,fontWeight:900,letterSpacing:2},links:{display:'flex',gap:8},link:{border:'1px solid #303030',background:'#151515',color:'#fff',borderRadius:999,padding:'9px 13px',cursor:'pointer',fontWeight:800},overlay:{position:'fixed',inset:0,zIndex:10000,background:'#050505f7',padding:'78px 18px 18px',overflowY:'auto'},panel:{maxWidth:1280,margin:'0 auto',background:'#0d0d0d',color:'#fff',border:'1px solid #292929',borderRadius:24,padding:24,boxShadow:'0 30px 100px #000'},header:{display:'flex',justifyContent:'space-between',gap:20},eyebrow:{fontSize:10,letterSpacing:3,color:'#888',fontWeight:900},title:{fontSize:'clamp(26px,4vw,52px)',margin:'6px 0'},sub:{color:'#888',margin:0},close:{width:44,height:44,borderRadius:12,border:'1px solid #333',background:'#171717',color:'#fff',fontSize:28,cursor:'pointer'},tabs:{display:'flex',gap:8,margin:'22px 0',flexWrap:'wrap'},tab:{padding:'11px 15px',border:'1px solid #333',borderRadius:999,background:'#171717',color:'#aaa',cursor:'pointer'},active:{padding:'11px 15px',border:'1px solid #fff',borderRadius:999,background:'#fff',color:'#000',cursor:'pointer',fontWeight:900},input:{width:'100%',boxSizing:'border-box',padding:13,borderRadius:12,border:'1px solid #333',background:'#171717',color:'#fff'},searchRow:{display:'flex',gap:12,alignItems:'center',marginBottom:14},count:{color:'#777',whiteSpace:'nowrap'},grid:{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))',gap:12},card:{background:'#151515',border:'1px solid #292929',borderRadius:16,padding:16,display:'grid',gap:7},crown:{fontSize:36},cardSpan:{color:'#aaa'},action:{marginTop:7,padding:'9px 11px',border:0,borderRadius:10,background:'#fff',color:'#000',fontWeight:900,cursor:'pointer'},modelGrid:{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(150px,1fr))',gap:12},modelCard:{background:'#151515',border:'1px solid #292929',borderRadius:14,overflow:'hidden'},img:{width:'100%',height:220,objectFit:'cover',display:'block'},meta:{padding:10,display:'grid',gap:6},notice:{padding:12,borderRadius:12,background:'#151515',color:'#888',marginBottom:12},pagination:{display:'flex',justifyContent:'center',alignItems:'center',gap:18,marginTop:20},pageBtn:{padding:'10px 14px',border:'1px solid #333',background:'#171717',color:'#fff',borderRadius:10,cursor:'pointer'},selected:{marginTop:18,padding:14,borderRadius:12,border:'1px solid #3d3d3d',background:'#151515',display:'grid',gap:4},footer:{color:'#666',fontSize:11,lineHeight:1.5,marginTop:18}}
