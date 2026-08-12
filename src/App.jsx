import React, { useState, useRef, useEffect } from 'react';

/* ─── SAMPLE WARDROBE URLS ────────────────────────────────────────── */
const imgBeigeJacket      = '/samples/beige-moto-jacket-navy-dress.jpg';
const imgBlackCropMaxi    = '/samples/black-crop-top-maxi-skirt.jpg';
const imgBlackCropSkirt   = '/samples/black-crop-top-skirt-set.jpg';
const imgBlueHoodie       = '/samples/blue-oversized-hoodie.jpg';
const imgCreamHoodie      = '/samples/cream-oversized-hoodie.jpg';
const imgDenimShirt       = '/samples/denim-shirt-beige-trousers-outfit.jpg';
const imgMensBlackHoodie  = '/samples/mens-black-hoodie.jpg';
const imgGeometricShirt   = '/samples/mens-geometric-print-shirt.jpg';
const imgWhiteTshirt      = '/samples/mens-white-tshirt-jeans.jpg';
const imgPinkSweater      = '/samples/pink-sweater-navy-jeans-outfit.jpg';
const imgTealBlazer       = '/samples/teal-blazer-grey-jeans.jpg';
const imgTealTrio         = '/samples/teal-khaki-black-dresses-trio.jpg';
const imgVintageDenim     = '/samples/vintage-denim-jacket.jpg';
const imgWhiteKnit        = '/samples/white-knit-flare-jeans-outfit.jpg';
const imgWhiteShirt       = '/samples/white-shirt-long-sleeve.webp';
const imgYellowTop        = '/samples/yellow-top-brown-culottes-outfit.jpg';

import {
  Sparkles, Image as ImageIcon, Loader2, Download,
  Scissors, ShoppingBag, User, Upload, Layers, Trash2,
  Maximize2, RefreshCw, X, Camera, Palette, Leaf, FileText,
  Bell, BellRing, Activity, Wand2, ChevronRight,
  Zap, ArrowRight, Cpu, Plus
} from 'lucide-react';

/* ─── CONFIG ──────────────────────────────────────────────────────── */
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "";
const GEMINI_MODEL   = import.meta.env.VITE_GEMINI_MODEL   || "gemini-2.5-flash";
// On Vercel the API functions are co-hosted at the same origin, so the
// default is "" (relative URLs like /api/try-on).  Override with
// VITE_BACKEND_URL only when running a separate backend (e.g. local dev).
const BACKEND_URL    = import.meta.env.VITE_BACKEND_URL    ?? "";

/* ─── STORAGE ─────────────────────────────────────────────────────── */
const StorageService = {
  getCollections: () => JSON.parse(localStorage.getItem('ai_fashion_collections') || '[]'),
  saveDesign: (design) => {
    const cols = StorageService.getCollections();
    const nd   = { ...design, id: Date.now(), isTracking: false };
    localStorage.setItem('ai_fashion_collections', JSON.stringify([nd, ...cols]));
    return nd;
  },
  deleteDesign: (id) => {
    localStorage.setItem('ai_fashion_collections',
      JSON.stringify(StorageService.getCollections().filter(d => d.id !== id)));
  },
  toggleTrack: (id) => {
    const updated = StorageService.getCollections().map(d =>
      d.id === id ? { ...d, isTracking: !d.isTracking } : d);
    localStorage.setItem('ai_fashion_collections', JSON.stringify(updated));
    return updated;
  }
};

const cleanJSON = (text) => {
  try { const m = text.match(/```(?:json)?\n([\s\S]*?)\n```/); return m ? m[1] : text; }
  catch { return text; }
};

/* ─── AI SERVICES ─────────────────────────────────────────────────── */
const FashionIntelligenceService = {
  async extractSpecification(prompt) {
    if (!GEMINI_API_KEY) return { optimized_image_prompt: prompt };
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;
      const payload = {
        contents: [{ parts: [{ text: `Extract fashion details to JSON: ${prompt}. Schema: {"category":"","fabric":"","colors":["hex"],"sustainability_score":0,"budget":{"maximum":0},"garment_description":""}` }] }],
        generationConfig: { responseMimeType: "application/json" }
      };
      const res  = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      return JSON.parse(cleanJSON(data.candidates[0].content.parts[0].text));
    } catch { return { optimized_image_prompt: prompt }; }
  }
};

/**
 * Build a concise garment description for IDM-VTON from available spec fields.
 * Falls back to the raw prompt if the spec is too sparse.
 * @param {object|null} spec  - Gemini-extracted fashion spec
 * @param {string}      prompt - Original user prompt
 * @returns {string}
 */
function buildGarmentDescription(spec, prompt) {
  if (spec?.garment_description) return spec.garment_description.trim().slice(0, 200);
  const parts = [];
  if (spec?.fabric)   parts.push(spec.fabric);
  if (spec?.category) parts.push(spec.category);
  if (parts.length >= 2) return parts.join(' ').slice(0, 200);
  // Fall back: use first 120 chars of the prompt as a rough description
  return prompt.trim().slice(0, 120);
}

/* ─── IMAGE MODELS ────────────────────────────────────────────────── */
export const IMAGE_MODELS = [
  { id: "@cf/black-forest-labs/flux-1-schnell",          label: "FLUX.1 Schnell", provider: "Cloudflare", badge: "Fast",    badgeColor: "text-sky-400 bg-sky-400/10 border-sky-400/20",       description: "Best quality/speed for fashion renders", default: true  },
  { id: "@cf/stabilityai/stable-diffusion-xl-base-1.0",  label: "SDXL Base 1.0",  provider: "Cloudflare", badge: "Detail",  badgeColor: "text-violet-400 bg-violet-400/10 border-violet-400/20", description: "Higher detail, slightly slower",          default: false },
  { id: "@cf/lykon/dreamshaper-8-lcm",                   label: "DreamShaper 8",  provider: "Cloudflare", badge: "Art",     badgeColor: "text-rose-400 bg-rose-400/10 border-rose-400/20",     description: "Painterly, creative fashion illustrations", default: false },
  { id: "@cf/bytedance/stable-diffusion-xl-lightning",   label: "SDXL Lightning", provider: "Cloudflare", badge: "⚡ Fast", badgeColor: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20", description: "Ultra-fast 4-step generation",          default: false },
];

const ImageGenerationService = {
  async generate(optimizedPrompt, modelId = null) {
    try {
      const body = { prompt: optimizedPrompt };
      if (modelId) body.model = modelId;
      const res = await fetch(`${BACKEND_URL}/api/design`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (res.ok) { const data = await res.json(); if (data.success && data.image) return data.image; }
      else { const err = await res.json().catch(() => ({})); if (res.status !== 503) console.warn('[ImageGen] CF error:', err?.error?.code); }
    } catch (e) { console.warn('[ImageGen] /api/design unreachable:', e.message); }
    try {
      const res = await fetch(`${BACKEND_URL}/api/generate-image`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: optimizedPrompt }) });
      if (res.ok) { const data = await res.json(); if (data.image_base64) return data.image_base64; }
      else { const err = await res.json().catch(() => ({})); if (err?.detail?.fallback_url) return err.detail.fallback_url; }
    } catch (e) { console.warn('[ImageGen] /api/generate-image unreachable:', e.message); }
    return null;
  }
};

/* ─── PRODUCT SEARCH SERVICE ──────────────────────────────────── */
// Calls the FastAPI backend /api/products/search endpoint.
// The RapidAPI key lives ONLY in the backend — never here.
const ProductSearchService = {
  /**
   * Build a plain-English query from the Gemini fashion spec, then ask
   * the backend for real H&M product recommendations.
   *
   * @param {object} spec - Gemini-extracted fashion specification
   * @param {string} rawPrompt - Original user prompt (fallback query)
   * @returns {Promise<Array>} Array of normalised product objects
   */
  async searchSimilarProducts(spec, rawPrompt = '') {
    try {
      // ── Build query from spec fields ──────────────────────────────────────
      const parts = [];
      if (spec?.fabric)   parts.push(spec.fabric);
      if (spec?.colors?.length) {
        // Convert hex → generic colour name isn't reliable; skip hex values
        // Use only if the prompt already contains a plain colour word
        const colorWords = ['black', 'white', 'red', 'blue', 'green', 'pink',
          'yellow', 'purple', 'orange', 'brown', 'grey', 'gray', 'navy',
          'teal', 'cream', 'beige', 'maroon', 'coral', 'indigo', 'gold'];
        const promptLower = rawPrompt.toLowerCase();
        const found = colorWords.find(c => promptLower.includes(c));
        if (found) parts.push(found);
      }
      if (spec?.category) parts.push(spec.category);

      const query = parts.length >= 2
        ? parts.join(' ')
        : rawPrompt.trim().slice(0, 100) || 'fashion';

      // ── Build URL with optional filters ───────────────────────────────────
      const params = new URLSearchParams({ query, limit: '5' });
      if (spec?.category)              params.set('category', spec.category);
      if (spec?.budget?.maximum > 0)   params.set('budget',   String(spec.budget.maximum));

      // Extract a single colour word for backend scoring
      const colorWords2 = ['black','white','red','blue','green','pink','yellow',
        'purple','orange','brown','grey','gray','navy','teal','cream','beige',
        'maroon','coral','indigo','gold'];
      const promptLower2 = rawPrompt.toLowerCase();
      const colorHint = colorWords2.find(c => promptLower2.includes(c));
      if (colorHint) params.set('color', colorHint);

      const res = await fetch(`${BACKEND_URL}/api/products/search?${params}`);

      if (res.status === 503) {
        // Backend not configured — silent fail (no fake data)
        console.info('[Products] Backend not configured for product search.');
        return [];
      }
      if (!res.ok) {
        console.warn('[Products] /api/products/search returned', res.status);
        return [];
      }

      const data = await res.json();
      return Array.isArray(data.products) ? data.products : [];
    } catch (e) {
      console.warn('[Products] request failed:', e.message);
      return [];
    }
  },
};

/* ─── ONLINE GARMENTS FOR QUICK-PICK IN TRY-ON ───────────────────── */
// Stable Unsplash photo URLs — clean garment / outfit shots on plain or
// minimal backgrounds, ideal for the IDM-VTON model.
const ONLINE_GARMENTS = [
  {
    id: "og1",
    label: "White Oversized Tee",
    category: "Casual",
    url: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
  },
  {
    id: "og2",
    label: "Classic Black Dress",
    category: "Dress",
    url: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80",
  },
  {
    id: "og3",
    label: "Navy Blazer",
    category: "Formal",
    url: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&q=80",
  },
  {
    id: "og4",
    label: "Olive Cargo Jacket",
    category: "Jacket",
    url: "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80",
  },
  {
    id: "og5",
    label: "Grey Hoodie",
    category: "Casual",
    url: "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&q=80",
  },
  {
    id: "og6",
    label: "Floral Midi Dress",
    category: "Dress",
    url: "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80",
  },
  {
    id: "og7",
    label: "Striped Linen Shirt",
    category: "Casual",
    url: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&q=80",
  },
  {
    id: "og8",
    label: "Slim-Fit Jeans",
    category: "Casual",
    url: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80",
  },
  {
    id: "og9",
    label: "Red Turtleneck",
    category: "Casual",
    url: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&q=80",
  },
  {
    id: "og10",
    label: "Beige Trench Coat",
    category: "Jacket",
    url: "https://images.unsplash.com/photo-1548454782-15b189d129ab?w=400&q=80",
  },
  {
    id: "og11",
    label: "Pastel Kurta",
    category: "Ethnic",
    url: "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=400&q=80",
  },
  {
    id: "og12",
    label: "Denim Jacket",
    category: "Jacket",
    url: "https://images.unsplash.com/photo-1542295669297-4d352b042bca?w=400&q=80",
  },
];

/* ─── WARDROBE DATA ───────────────────────────────────────────────── */
const sampleWardrobe = [
  { id: 1,  label: "Beige Moto Jacket",          image: imgBeigeJacket,     category: "Jacket" },
  { id: 2,  label: "Black Crop Top & Maxi",      image: imgBlackCropMaxi,   category: "Set"    },
  { id: 3,  label: "Black Crop & Skirt Set",     image: imgBlackCropSkirt,  category: "Set"    },
  { id: 4,  label: "Blue Oversized Hoodie",      image: imgBlueHoodie,      category: "Casual" },
  { id: 5,  label: "Cream Oversized Hoodie",     image: imgCreamHoodie,     category: "Casual" },
  { id: 6,  label: "Denim Shirt & Trousers",     image: imgDenimShirt,      category: "Casual" },
  { id: 7,  label: "Men's Black Hoodie",         image: imgMensBlackHoodie, category: "Men"    },
  { id: 8,  label: "Geometric Print Shirt",      image: imgGeometricShirt,  category: "Men"    },
  { id: 9,  label: "White T-Shirt & Jeans",      image: imgWhiteTshirt,     category: "Men"    },
  { id: 10, label: "Pink Sweater & Navy Jeans",  image: imgPinkSweater,     category: "Casual" },
  { id: 11, label: "Teal Blazer & Grey Jeans",   image: imgTealBlazer,      category: "Formal" },
  { id: 12, label: "Teal, Khaki & Black Trio",   image: imgTealTrio,        category: "Dress"  },
  { id: 13, label: "Vintage Denim Jacket",       image: imgVintageDenim,    category: "Jacket" },
  { id: 14, label: "White Knit & Flare Jeans",   image: imgWhiteKnit,       category: "Casual" },
  { id: 15, label: "White Long Sleeve Shirt",    image: imgWhiteShirt,      category: "Formal" },
  { id: 16, label: "Yellow Top & Brown Culotte", image: imgYellowTop,       category: "Casual" },
];

const CAT_COLORS = {
  Jacket: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  Set:    "bg-violet-500/20 text-violet-300 border-violet-500/30",
  Casual: "bg-sky-500/20 text-sky-300 border-sky-500/30",
  Men:    "bg-neutral-500/20 text-neutral-300 border-neutral-500/30",
  Formal: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Dress:  "bg-rose-500/20 text-rose-300 border-rose-500/30",
  Ethnic: "bg-orange-500/20 text-orange-300 border-orange-500/30",
};

const QUICK_PROMPTS = [
  { label: "Saree",   prompt: "An elegant silk saree with contemporary geometric border in deep teal and gold" },
  { label: "Kurta",   prompt: "A minimalist cotton kurta with subtle white embroidery, earthy tones, under ₹2500" },
  { label: "Blazer",  prompt: "A structured oversized blazer in camel wool with gold buttons, street style" },
  { label: "Co-ord",  prompt: "A linen co-ord set in soft terracotta, relaxed fit, summer-ready" },
  { label: "Lehenga", prompt: "A lightweight lehenga in blush pink with intricate mirror work and modern silhouette" },
];

/* ════════════════════════════════════════════════════════════════════
   MAIN APP
═══════════════════════════════════════════════════════════════════ */
export default function App() {
  const [activeTab, setActiveTab]         = useState('runway');
  const [prompt, setPrompt]               = useState('');
  const [selectedModel, setSelectedModel] = useState(IMAGE_MODELS.find(m => m.default).id);
  // designJob.garmentSource: 'design' | 'wardrobe' | 'online'
  // designJob.garmentDescription: string sent to IDM-VTON as garment_des
  const [designJob, setDesignJob]         = useState({ status: 'idle', spec: null, image: null, products: [], garmentSource: null, garmentDescription: '' });
  const [expandedImage, setExpandedImage] = useState(null);
  const [showTechPack, setShowTechPack]   = useState(false);
  const [personImage, setPersonImage]     = useState(null);
  const [personFile, setPersonFile]       = useState(null);   // raw File for FormData
  const [tryOnJob, setTryOnJob]           = useState({ status: 'idle', resultImage: null, statusMsg: '' });
  const [savedDesigns, setSavedDesigns]   = useState([]);
  const [savePulse, setSavePulse]         = useState(false);
  const [wardrobeFilter, setWardrobeFilter] = useState('All');
  const fileInputRef  = useRef(null);
  const promptRef     = useRef(null);

  useEffect(() => { setSavedDesigns(StorageService.getCollections()); }, []);

  /* ── scroll lock when modal open ── */
  useEffect(() => {
    document.body.style.overflow = (expandedImage || showTechPack) ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [expandedImage, showTechPack]);

  const handleGenerateDesign = async (overridePrompt = null) => {
    const p = overridePrompt || prompt;
    if (!p.trim()) return;
    setPrompt(p);
    if (activeTab !== 'design') setActiveTab('design');
    setDesignJob({ status: 'processing', spec: null, image: null, products: [], garmentSource: null, garmentDescription: '' });
    try {
      const spec = await FashionIntelligenceService.extractSpecification(p);
      const [image, products] = await Promise.all([
        ImageGenerationService.generate(spec.optimized_image_prompt || p, selectedModel),
        ProductSearchService.searchSimilarProducts(spec, p),
      ]);
      if (!image) {
        setDesignJob({ status: 'failed', spec: null, image: null, products: [], garmentSource: null, garmentDescription: '' });
      } else {
        const garmentDescription = buildGarmentDescription(spec, p);
        setDesignJob({ status: 'completed', spec, image, products, prompt: p, garmentSource: 'design', garmentDescription });
      }
    } catch {
      setDesignJob({ status: 'failed', spec: null, image: null, products: [], garmentSource: null, garmentDescription: '' });
    }
  };

  const handleSaveDesign = () => {
    StorageService.saveDesign({ image: designJob.image, prompt: designJob.prompt, spec: designJob.spec });
    setSavedDesigns(StorageService.getCollections());
    setSavePulse(true);
    setTimeout(() => setSavePulse(false), 1400);
  };

  const handlePersonUpload = e => {
    const file = e.target.files[0];
    if (!file) return;
    setPersonFile(file);
    const reader = new FileReader();
    reader.onload = ev => setPersonImage(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleTryOn = async () => {
    if (!personFile || !designJob.image) return;

    setTryOnJob({ status: 'processing', resultImage: null, statusMsg: 'Uploading images…' });

    try {
      // Convert the garment data-URI or URL back to a Blob for FormData
      const garmentResp = await fetch(designJob.image);
      const garmentBlob = await garmentResp.blob();

      setTryOnJob(j => ({ ...j, statusMsg: 'Queuing AI try-on…' }));

      const form = new FormData();
      form.append('person',  personFile,  personFile.name  || 'person.jpg');
      form.append('garment', garmentBlob, 'garment.jpg');
      // Pass the garment description so IDM-VTON gets a meaningful garment_des value
      if (designJob.garmentDescription) {
        form.append('garment_description', designJob.garmentDescription);
      }

      setTryOnJob(j => ({ ...j, statusMsg: 'AI is processing — this may take ~30–60 s…' }));

      const res = await fetch(`${BACKEND_URL}/api/try-on`, {
        method: 'POST',
        body: form,
      });

      const data = await res.json();

      if (res.ok && data.success && data.image) {
        setTryOnJob({ status: 'completed', resultImage: data.image, statusMsg: '' });
      } else {
        const msg = data?.error?.message || 'Virtual try-on failed. Please try again.';
        setTryOnJob({ status: 'failed', resultImage: null, statusMsg: msg });
      }
    } catch (err) {
      console.warn('[TryOn] request failed:', err.message);
      setTryOnJob({ status: 'failed', resultImage: null, statusMsg: 'Connection error — is the backend running?' });
    }
  };

  const NAV_TABS = [
    { id: 'runway',     label: 'Runway',   icon: Activity  },
    { id: 'design',     label: 'Studio',   icon: Sparkles  },
    { id: 'tryon',      label: 'Try-On',   icon: User      },
    { id: 'collection', label: 'Collection', icon: Layers  },
  ];

  /* ────────────────────────────────────────────────────────────────
     RENDER
  ──────────────────────────────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-[#050505] text-neutral-100 font-sans antialiased selection:bg-violet-900/40">

      {/* ── GLOBAL STYLES ─────────────────────────────────────────── */}
      <style>{`
        @keyframes fade-up   { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
        @keyframes fade-in   { from { opacity:0 } to { opacity:1 } }
        @keyframes shimmer   { from { background-position:200% 0 } to { background-position:-200% 0 } }
        @keyframes pulse-dot { 0%,100% { opacity:1 } 50% { opacity:.3 } }
        .anim-fade-up  { animation: fade-up  .35s cubic-bezier(.16,1,.3,1) both }
        .anim-fade-in  { animation: fade-in  .25s ease both }
        .shimmer-bg {
          background: linear-gradient(90deg, #1a1a1a 25%, #252525 50%, #1a1a1a 75%);
          background-size: 200% 100%;
          animation: shimmer 1.6s infinite;
        }
        .glass {
          background: rgba(255,255,255,0.03);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
        }
        .card-hover {
          transition: transform .22s cubic-bezier(.16,1,.3,1), border-color .2s, box-shadow .2s;
        }
        .card-hover:hover {
          transform: translateY(-3px);
          box-shadow: 0 20px 60px rgba(0,0,0,.5);
        }
        textarea:focus { border-color: rgba(139,92,246,.5) !important; box-shadow: 0 0 0 3px rgba(139,92,246,.08); }
        ::-webkit-scrollbar { width:5px; height:5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background:#333; border-radius:9999px; }
      `}</style>

      {/* ── LIGHTBOX ──────────────────────────────────────────────── */}
      {expandedImage && (
        <div
          className="fixed inset-0 z-[300] bg-black/95 backdrop-blur-2xl flex items-center justify-center p-6 anim-fade-in"
          onClick={() => setExpandedImage(null)}
        >
          <button
            className="absolute top-5 right-5 w-10 h-10 bg-white/8 hover:bg-white/15 text-white rounded-full flex items-center justify-center transition-colors border border-white/10"
            onClick={() => setExpandedImage(null)}
          >
            <X size={18} />
          </button>
          <img
            src={expandedImage} alt="Expanded"
            className="max-w-[88vw] max-h-[88vh] rounded-2xl object-contain ring-1 ring-white/10 anim-fade-up"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}

      {/* ── TECH PACK MODAL ───────────────────────────────────────── */}
      {showTechPack && designJob.spec && (
        <div
          className="fixed inset-0 z-[300] bg-black/80 backdrop-blur-xl flex items-center justify-center p-5 anim-fade-in"
          onClick={() => setShowTechPack(false)}
        >
          <div
            className="bg-[#0d0d0d] border border-white/8 rounded-3xl w-full max-w-lg shadow-2xl anim-fade-up overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/6">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 bg-violet-500/15 rounded-lg flex items-center justify-center">
                  <FileText size={13} className="text-violet-400" />
                </div>
                <span className="font-semibold text-sm text-white">Tech Pack</span>
              </div>
              <button
                onClick={() => setShowTechPack(false)}
                className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-neutral-400 hover:text-white transition-colors"
              >
                <X size={14} />
              </button>
            </div>
            {/* Body */}
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Fabric",        value: designJob.spec.fabric || "—"          },
                  { label: "Category",      value: designJob.spec.category || "Apparel"  },
                  { label: "Color Palette", value: designJob.spec.colors?.join(", ") || "—" },
                  { label: "Est. Cost",     value: `₹${(designJob.spec.budget?.maximum * 0.4 || 0).toFixed(0)}` },
                ].map(f => (
                  <div key={f.label} className="bg-white/3 border border-white/6 rounded-xl p-3.5">
                    <span className="text-neutral-600 text-[10px] uppercase tracking-widest block mb-1.5">{f.label}</span>
                    <span className="text-neutral-200 text-sm font-medium leading-snug">{f.value}</span>
                  </div>
                ))}
              </div>
              {/* Eco bar */}
              <div className="bg-emerald-500/6 border border-emerald-500/15 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-emerald-400 font-medium flex items-center gap-1.5">
                    <Leaf size={11} /> Sustainability Score
                  </span>
                  <span className="text-sm font-bold text-emerald-300">{designJob.spec.sustainability_score || 80}/100</span>
                </div>
                <div className="h-1.5 bg-emerald-950/60 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full transition-all duration-700"
                    style={{ width: `${designJob.spec.sustainability_score || 80}%` }}
                  />
                </div>
              </div>
              <div className="bg-white/3 border border-white/6 rounded-xl p-4">
                <p className="text-[10px] text-neutral-600 uppercase tracking-widest mb-2">Construction Notes</p>
                <ul className="space-y-1.5 text-xs text-neutral-500 list-disc pl-4">
                  <li>Standard 1.5 cm seam allowance on all panels.</li>
                  <li>Eco-friendly dyes recommended for target score.</li>
                  <li className="text-neutral-700 italic line-clamp-1">"{designJob.prompt}"</li>
                </ul>
              </div>
              <button
                onClick={() => setShowTechPack(false)}
                className="w-full bg-white text-black py-3 rounded-xl text-sm font-semibold hover:bg-neutral-100 active:scale-[.98] transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── NAV ───────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-[#050505]/85 backdrop-blur-2xl border-b border-white/5">
        {/* Accent line */}
        <div className="h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
        <div className="max-w-7xl mx-auto px-5 h-14 flex items-center justify-between">

          {/* Logo */}
          <div className="flex items-center gap-2.5 select-none">
            <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center shadow-lg">
              <Scissors size={13} className="text-black" />
            </div>
            <div className="hidden sm:flex items-baseline gap-1.5">
              <span className="font-bold text-[15px] tracking-tight text-white">Studio</span>
              <span className="text-[15px] font-light text-neutral-500 tracking-tight">AI</span>
            </div>
            <span className="text-[9px] font-bold text-violet-400 bg-violet-400/10 border border-violet-400/20 px-1.5 py-0.5 rounded tracking-widest hidden sm:inline">BETA</span>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-0.5 p-1 bg-white/4 border border-white/6 rounded-xl">
            {NAV_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium flex items-center gap-1.5 transition-all duration-200 whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'bg-white text-black shadow-md'
                    : 'text-neutral-500 hover:text-neutral-200 hover:bg-white/5'}`}
              >
                <tab.icon size={12} />
                <span className="hidden sm:inline">{tab.label}</span>
                {tab.id === 'collection' && savedDesigns.length > 0 && activeTab !== 'collection' && (
                  <span className="absolute -top-1.5 -right-1.5 bg-violet-500 text-white text-[8px] font-bold rounded-full min-w-[14px] h-3.5 flex items-center justify-center px-0.5">
                    {savedDesigns.length > 9 ? '9+' : savedDesigns.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* ── MAIN ──────────────────────────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-5 py-8">

        {/* ══════════════════════════ RUNWAY ══════════════════════════ */}
        {activeTab === 'runway' && (
          <div className="space-y-12 anim-fade-up">

            {/* ── HERO ─────────────────────────────────────────────── */}
            <div className="relative rounded-3xl overflow-hidden border border-white/6 min-h-[360px] flex items-center">
              {/* layered bg */}
              <div className="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-[#080808] to-[#080808]" />
              <div className="absolute inset-0 opacity-[0.025]"
                style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #fff 1px, transparent 0)', backgroundSize: '28px 28px' }} />
              {/* glow orb */}
              <div className="absolute -top-32 -left-32 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
              <div className="absolute -bottom-32 right-0 w-72 h-72 bg-indigo-600/8 rounded-full blur-3xl pointer-events-none" />

              <div className="relative z-10 w-full px-8 md:px-16 py-14 text-center">
                {/* Badge */}
                <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 text-violet-300 text-[11px] font-semibold px-3.5 py-1.5 rounded-full mb-6 tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-[pulse-dot_1.5s_ease_infinite]" />
                  AI-Powered Fashion Intelligence
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-5 leading-[1.05] tracking-tighter">
                  Design.{' '}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">
                    Try.
                  </span>{' '}
                  Wear.
                </h1>
                <p className="text-neutral-400 text-base md:text-lg max-w-xl mx-auto mb-10 leading-relaxed">
                  Describe any outfit in plain language — our AI renders it, extracts specs, and lets you try it on.
                </p>

                {/* Inline prompt bar */}
                <form
                  onSubmit={e => { e.preventDefault(); handleGenerateDesign(); }}
                  className="max-w-2xl mx-auto flex gap-2 items-center bg-white/5 border border-white/10 rounded-2xl p-2 focus-within:border-violet-500/40 transition-colors"
                >
                  <Sparkles size={16} className="text-neutral-600 ml-2 shrink-0" />
                  <input
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    placeholder="e.g. A minimalist navy kurta with gold embroidery…"
                    className="flex-1 bg-transparent text-sm text-neutral-200 placeholder:text-neutral-700 focus:outline-none py-1.5 min-w-0"
                  />
                  <button
                    type="submit"
                    disabled={!prompt.trim() || designJob.status === 'processing'}
                    className="shrink-0 bg-white text-black text-xs font-bold px-4 py-2.5 rounded-xl hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed active:scale-95 transition-all flex items-center gap-1.5"
                  >
                    {designJob.status === 'processing'
                      ? <><Loader2 size={12} className="animate-spin" /> Generating</>
                      : <><Wand2 size={12} /> Generate</>}
                  </button>
                </form>

                {/* Quick prompts */}
                <div className="flex flex-wrap gap-2 justify-center mt-5">
                  {QUICK_PROMPTS.map(q => (
                    <button
                      key={q.label}
                      onClick={() => { setPrompt(q.prompt); setActiveTab('design'); setTimeout(() => handleGenerateDesign(q.prompt), 0); }}
                      className="text-[11px] text-neutral-500 hover:text-neutral-200 bg-white/3 hover:bg-white/7 border border-white/6 hover:border-white/12 px-3 py-1.5 rounded-full transition-all"
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* ── WARDROBE SECTION ──────────────────────────────────── */}
            <div>
              {/* Section header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
                    <div className="w-6 h-6 bg-violet-500/15 rounded-lg flex items-center justify-center">
                      <Layers size={13} className="text-violet-400" />
                    </div>
                    Sample Wardrobe
                  </h2>
                  <p className="text-xs text-neutral-600 mt-1">{sampleWardrobe.length} pieces — click any item to Try-On</p>
                </div>
              </div>

              {/* Filter pills */}
              <div className="flex flex-wrap gap-2 mb-6">
                {['All', ...Array.from(new Set(sampleWardrobe.map(w => w.category)))].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setWardrobeFilter(cat)}
                    className={`text-[11px] font-semibold px-3.5 py-1.5 rounded-full border transition-all duration-200
                      ${wardrobeFilter === cat
                        ? 'bg-white text-black border-white shadow-md'
                        : 'bg-white/3 text-neutral-500 border-white/8 hover:text-white hover:border-white/20 hover:bg-white/6'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              {/* Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                {sampleWardrobe
                  .filter(w => wardrobeFilter === 'All' || w.category === wardrobeFilter)
                  .map((item, i) => (
                    <div
                      key={item.id}
                      className="group relative bg-neutral-900/50 border border-white/6 rounded-2xl overflow-hidden cursor-pointer card-hover"
                      style={{ animationDelay: `${i * 30}ms` }}
                      onClick={() => {
                        setDesignJob(prev => ({
                          ...prev,
                          image: item.image,
                          garmentSource: 'wardrobe',
                          garmentDescription: item.label,
                        }));
                        setActiveTab('tryon');
                      }}
                    >
                      {/* Image */}
                      <div className="aspect-[3/4] overflow-hidden bg-neutral-950">
                        <img
                          src={item.image}
                          alt={item.label}
                          className="w-full h-full object-cover group-hover:scale-[1.06] transition-transform duration-500"
                          onError={e => { e.target.style.display = 'none'; }}
                        />
                      </div>

                      {/* Category badge */}
                      <span className={`absolute top-2.5 left-2.5 text-[9px] font-bold px-2 py-0.5 rounded-full border backdrop-blur-sm ${CAT_COLORS[item.category] || 'bg-neutral-500/20 text-neutral-300 border-neutral-500/30'}`}>
                        {item.category}
                      </span>

                      {/* Gradient overlay */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                      {/* Hover content */}
                      <div className="absolute bottom-0 inset-x-0 p-3 translate-y-3 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
                        <p className="text-[11px] text-white font-semibold leading-snug mb-2 line-clamp-1">{item.label}</p>
                        <div className="flex items-center justify-center gap-1.5 w-full bg-white/15 backdrop-blur-md text-white border border-white/20 py-1.5 rounded-lg text-[10px] font-bold hover:bg-white hover:text-black transition-all">
                          <User size={9} /> Try On
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

          </div>
        )}

        {/* ══════════════════════════ STUDIO ══════════════════════════ */}
        {activeTab === 'design' && (
          <div className="anim-fade-up">

            {/* Top prompt bar */}
            <div className="bg-white/3 border border-white/8 rounded-2xl p-5 mb-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Wand2 size={14} className="text-violet-400" /> Design Prompt
                </h2>
                <button
                  onClick={() => setPrompt("A navy blue velvet blazer with intricate gold zari embroidery on the lapel, formal Indian style.")}
                  className="flex items-center gap-1.5 text-[11px] text-neutral-500 hover:text-neutral-200 bg-white/4 border border-white/8 hover:border-white/15 px-2.5 py-1.5 rounded-lg transition-all"
                >
                  <Camera size={10} /> Sample
                </button>
              </div>

              <form onSubmit={e => { e.preventDefault(); handleGenerateDesign(); }} className="space-y-3">
                <textarea
                  ref={promptRef}
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  placeholder="Describe your design in detail — fabric, colour, occasion, style…"
                  className="w-full h-28 p-4 bg-black/40 border border-white/8 rounded-xl resize-none focus:outline-none text-sm text-neutral-200 placeholder:text-neutral-700 transition-all leading-relaxed"
                  required
                />

                {/* ── AI Model card-picker ──────────────────────────── */}
                <div>
                  <p className="text-[10px] text-neutral-600 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <Cpu size={9} /> Choose AI Model
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {IMAGE_MODELS.map(m => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setSelectedModel(m.id)}
                        className={`relative flex flex-col gap-1.5 p-3 rounded-xl border text-left transition-all duration-150 active:scale-[.97]
                          ${selectedModel === m.id
                            ? 'bg-white/8 border-white/20 ring-1 ring-white/15'
                            : 'bg-black/30 border-white/6 hover:border-white/14 hover:bg-white/4'}`}
                      >
                        {/* Selected dot */}
                        {selectedModel === m.id && (
                          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-violet-400" />
                        )}
                        <span className={`self-start text-[9px] font-bold px-1.5 py-0.5 rounded border ${m.badgeColor}`}>
                          {m.badge}
                        </span>
                        <span className="text-[11px] font-semibold text-neutral-200 leading-snug">{m.label}</span>
                        <span className="text-[10px] text-neutral-600 leading-snug">{m.description}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Generate button */}
                <button
                  type="submit"
                  disabled={designJob.status === 'processing'}
                  className="w-full bg-white text-black py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-neutral-100 disabled:opacity-40 active:scale-[.98] transition-all"
                >
                  {designJob.status === 'processing'
                    ? <><Loader2 size={15} className="animate-spin" /> Rendering…</>
                    : <><Sparkles size={15} /> Generate Design</>}
                </button>

                {/* Quick style chips */}
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  {QUICK_PROMPTS.map(q => (
                    <button
                      key={q.label}
                      type="button"
                      onClick={() => setPrompt(q.prompt)}
                      className="text-[11px] px-3 py-1 bg-white/3 border border-white/7 text-neutral-500 hover:text-white hover:border-white/15 rounded-full transition-all"
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </form>
            </div>

            {/* Output area */}
            {designJob.status === 'completed' && designJob.image ? (
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

                {/* Generated image — takes more space */}
                <div className="lg:col-span-3 bg-white/3 border border-white/8 rounded-2xl overflow-hidden group relative flex flex-col">
                  {/* Image action buttons */}
                  <div className="absolute top-3 right-3 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-200 z-10">
                    {[
                      { icon: RefreshCw, title: "Regenerate", action: () => handleGenerateDesign() },
                      { icon: Download,  title: "Download",   action: () => { const a = document.createElement('a'); a.href = designJob.image; a.download = 'design.png'; a.click(); } },
                      { icon: Maximize2, title: "Expand",     action: () => setExpandedImage(designJob.image) },
                    ].map(({ icon: Icon, title, action }) => (
                      <button
                        key={title}
                        onClick={action}
                        title={title}
                        className="w-8 h-8 bg-black/70 backdrop-blur-md text-white rounded-lg flex items-center justify-center hover:bg-black/90 border border-white/10 transition-colors"
                      >
                        <Icon size={13} />
                      </button>
                    ))}
                  </div>

                  {/* Image */}
                  <div className="flex-1 min-h-[380px] bg-neutral-950 overflow-hidden">
                    <img
                      src={designJob.image}
                      alt="Generated Design"
                      className="w-full h-full object-cover"
                      style={{ minHeight: 380 }}
                    />
                  </div>

                  {/* Info strip */}
                  {designJob.spec && (
                    <div className="p-5 border-t border-white/6 space-y-4">
                      <div className="grid grid-cols-2 gap-3">
                        {/* Palette */}
                        <div className="bg-black/30 border border-white/6 p-3.5 rounded-xl">
                          <p className="text-[10px] text-neutral-600 uppercase tracking-widest mb-2.5 flex items-center gap-1.5">
                            <Palette size={9} /> Palette
                          </p>
                          <div className="flex gap-1.5 flex-wrap">
                            {(designJob.spec.colors?.length
                              ? designJob.spec.colors.slice(0, 6)
                              : ['#334155', '#64748b', '#94a3b8']
                            ).map(c => (
                              <div key={c} className="w-6 h-6 rounded-full ring-2 ring-black/50 shadow-sm cursor-default" style={{ backgroundColor: c }} title={c} />
                            ))}
                          </div>
                        </div>
                        {/* Eco score */}
                        <div className="bg-black/30 border border-white/6 p-3.5 rounded-xl">
                          <p className="text-[10px] text-neutral-600 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                            <Leaf size={9} className="text-emerald-600" /> Eco Score
                          </p>
                          <div className="flex items-end gap-1">
                            <span className="text-2xl font-black text-emerald-400 leading-none">{designJob.spec.sustainability_score || '—'}</span>
                            {designJob.spec.sustainability_score && <span className="text-xs text-neutral-700 mb-0.5">/100</span>}
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2.5">
                        <button
                          onClick={handleSaveDesign}
                          className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all border active:scale-95
                            ${savePulse
                              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                              : 'bg-white/5 border-white/10 text-neutral-300 hover:bg-white/10 hover:text-white'}`}
                        >
                          {savePulse ? '✓ Saved to Collection' : 'Save Design'}
                        </button>
                        <button
                          onClick={() => setActiveTab('tryon')}
                          className="flex-1 py-2.5 rounded-xl text-xs font-bold bg-white text-black hover:bg-neutral-100 active:scale-95 transition-all"
                        >
                          Try On →
                        </button>
                      </div>
                      <button
                        onClick={() => setShowTechPack(true)}
                        className="w-full border border-dashed border-white/10 hover:border-white/20 text-neutral-600 hover:text-neutral-300 py-2.5 rounded-xl text-xs font-medium transition-all flex items-center justify-center gap-2"
                      >
                        <FileText size={11} /> View Tech Pack
                      </button>
                    </div>
                  )}
                </div>

                {/* Right panel: product recommendations + prompt recap */}
                <div className="lg:col-span-2 flex flex-col gap-5">

                  {/* ── Buy Similar — Real Product Recommendations ───────── */}
                  <div className="bg-white/3 border border-white/8 rounded-2xl overflow-hidden flex-1 flex flex-col">
                    {/* Header */}
                    <div className="px-5 py-4 border-b border-white/6 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-violet-500/15 rounded-lg flex items-center justify-center">
                          <ShoppingBag size={11} className="text-violet-400" />
                        </div>
                        <span className="text-sm font-bold text-white">Buy Similar</span>
                      </div>
                      {designJob.products?.length > 0 && (
                        <span className="text-[10px] text-neutral-600 bg-white/4 border border-white/8 px-2 py-0.5 rounded-full">
                          H&M via RapidAPI
                        </span>
                      )}
                    </div>

                    {/* Body */}
                    <div className="flex-1 overflow-y-auto">
                      {/* Loading state */}
                      {designJob.status === 'processing' ? (
                        <div className="flex flex-col items-center justify-center p-8 text-center h-full min-h-[160px]">
                          <div className="relative w-8 h-8 mb-3 mx-auto">
                            <div className="absolute inset-0 rounded-full border border-white/6" />
                            <div className="absolute inset-0 rounded-full border-t border-violet-500 animate-spin" />
                          </div>
                          <p className="text-xs text-neutral-500 font-medium">Finding matching fashion products…</p>
                        </div>

                      /* Has real products */
                      ) : designJob.products?.length > 0 ? (
                        <div className="divide-y divide-white/5">
                          {designJob.products.map((product, idx) => (
                            <div key={idx} className="flex gap-3 p-4 hover:bg-white/3 transition-colors group/prod">
                              {/* Product image */}
                              <div className="w-16 h-20 shrink-0 bg-neutral-900 rounded-xl overflow-hidden border border-white/6">
                                {product.image ? (
                                  <img
                                    src={product.image}
                                    alt={product.name}
                                    className="w-full h-full object-cover group-hover/prod:scale-105 transition-transform duration-300"
                                    onError={e => { e.target.style.display = 'none'; }}
                                  />
                                ) : (
                                  <div className="w-full h-full flex items-center justify-center">
                                    <ShoppingBag size={14} className="text-neutral-800" />
                                  </div>
                                )}
                              </div>

                              {/* Product info */}
                              <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                                <div>
                                  <p className="text-xs font-semibold text-neutral-200 leading-snug line-clamp-2 mb-1">
                                    {product.name}
                                  </p>
                                  <p className="text-[10px] text-neutral-600 mb-1.5">
                                    {product.brand || product.source}
                                  </p>
                                  <div className="flex items-center gap-2 flex-wrap">
                                    {product.price != null && (
                                      <span className="text-[11px] font-bold text-white">
                                        ₹{Number(product.price).toLocaleString('en-IN')}
                                      </span>
                                    )}
                                    {product.recommendation_score != null && (
                                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border
                                        ${product.recommendation_score >= 80
                                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25'
                                          : product.recommendation_score >= 55
                                          ? 'bg-sky-500/15 text-sky-400 border-sky-500/25'
                                          : 'bg-neutral-500/15 text-neutral-500 border-neutral-500/25'}`}>
                                        {product.recommendation_score}% match
                                      </span>
                                    )}
                                  </div>
                                </div>
                                {product.url && (
                                  <a
                                    href={product.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="mt-2 inline-flex items-center gap-1 text-[10px] font-semibold text-violet-400 hover:text-violet-300 transition-colors"
                                  >
                                    View Product <ArrowRight size={9} />
                                  </a>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>

                      /* No results after search completed */
                      ) : designJob.status === 'completed' ? (
                        <div className="flex flex-col items-center justify-center p-8 text-center h-full min-h-[160px]">
                          <div className="w-9 h-9 bg-white/4 border border-white/8 rounded-xl flex items-center justify-center mb-3 mx-auto">
                            <ShoppingBag size={14} className="text-neutral-700" />
                          </div>
                          <p className="text-xs text-neutral-600 mb-0.5">No matching products found.</p>
                          <p className="text-[10px] text-neutral-800 leading-relaxed">
                            Try changing the category, colour, or budget in your prompt.
                          </p>
                        </div>

                      /* Idle — nothing generated yet */
                      ) : (
                        <div className="flex flex-col items-center justify-center p-8 text-center h-full min-h-[160px]">
                          <div className="w-9 h-9 bg-white/4 border border-white/8 rounded-xl flex items-center justify-center mb-3 mx-auto">
                            <ShoppingBag size={14} className="text-neutral-700" />
                          </div>
                          <p className="text-xs text-neutral-600">Generate a design to see real product recommendations.</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Prompt recap */}
                  <div className="bg-white/3 border border-white/8 rounded-2xl p-5">
                    <p className="text-[10px] text-neutral-600 uppercase tracking-widest mb-2">Your Prompt</p>
                    <p className="text-xs text-neutral-400 leading-relaxed line-clamp-4">{designJob.prompt}</p>
                    {designJob.spec?.category && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {[designJob.spec.category, designJob.spec.fabric].filter(Boolean).map(v => (
                          <span key={v} className="text-[10px] text-neutral-500 bg-white/4 border border-white/8 px-2 py-0.5 rounded-full">{v}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              /* ── Empty / loading state ── */
              <div className="bg-white/2 border border-white/6 rounded-2xl min-h-[440px] flex flex-col items-center justify-center text-center p-10">
                {designJob.status === 'processing' ? (
                  <div className="space-y-5">
                    {/* Animated rings */}
                    <div className="relative mx-auto w-14 h-14">
                      <div className="absolute inset-0 rounded-full border border-white/6" />
                      <div className="absolute inset-0 rounded-full border-t border-violet-500 animate-spin" />
                      <div className="absolute inset-2 rounded-full border border-white/4" />
                      <div className="absolute inset-2 rounded-full border-t border-indigo-400 animate-spin" style={{ animationDuration: '1.4s', animationDirection: 'reverse' }} />
                    </div>
                    <div className="space-y-1.5">
                      <p className="text-sm text-neutral-300 font-medium">Generating your design…</p>
                      <p className="text-xs text-neutral-700">This may take 10–30 seconds</p>
                    </div>
                    {/* Shimmer bar */}
                    <div className="w-48 h-1.5 rounded-full overflow-hidden mx-auto">
                      <div className="h-full shimmer-bg rounded-full" />
                    </div>
                  </div>
                ) : designJob.status === 'failed' ? (
                  <div className="space-y-4">
                    <div className="w-12 h-12 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center justify-center mx-auto">
                      <X size={20} className="text-red-400" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-neutral-300 font-medium">Generation failed</p>
                      <p className="text-xs text-neutral-700">Check your backend connection and try again</p>
                    </div>
                    <button
                      onClick={() => handleGenerateDesign()}
                      className="text-xs text-violet-400 hover:text-violet-300 bg-violet-400/10 border border-violet-400/20 px-4 py-2 rounded-lg transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-12 h-12 bg-white/4 border border-white/8 rounded-2xl flex items-center justify-center mx-auto">
                      <Sparkles size={20} className="text-neutral-700" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-neutral-400 font-medium">Your design will appear here</p>
                      <p className="text-xs text-neutral-700">Fill in the prompt above and hit Generate</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ══════════════════════════ TRY-ON ══════════════════════════ */}
        {activeTab === 'tryon' && (
          <div className="space-y-6 anim-fade-up">

            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Virtual Try-On</h2>
                <p className="text-xs text-neutral-600 mt-0.5">Upload your photo, pick a garment, then process</p>
              </div>
              {!designJob.image && (
                <button
                  onClick={() => setActiveTab('design')}
                  className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1.5 bg-violet-400/8 border border-violet-400/20 px-3.5 py-2 rounded-xl transition-colors"
                >
                  <Sparkles size={11} /> Generate a design first
                </button>
              )}
            </div>

            <div className="bg-white/2 border border-white/6 rounded-2xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Step 1 — Photo */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2.5 mb-1">
                    <div className="w-6 h-6 bg-white/8 border border-white/12 rounded-full flex items-center justify-center text-[11px] font-bold text-neutral-400">1</div>
                    <p className="text-xs font-semibold text-neutral-400 uppercase tracking-widest">Your Photo</p>
                  </div>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="aspect-[3/4] bg-black/30 border-2 border-dashed border-white/8 hover:border-white/20 rounded-2xl flex items-center justify-center cursor-pointer overflow-hidden relative transition-all group/up"
                  >
                    {personImage ? (
                      <img src={personImage} className="w-full h-full object-cover" alt="Person" />
                    ) : (
                      <div className="text-center space-y-3 p-4">
                        <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center mx-auto group-hover/up:bg-white/10 transition-colors">
                          <Upload size={16} className="text-neutral-700 group-hover/up:text-neutral-400 transition-colors" />
                        </div>
                        <div>
                          <p className="text-xs text-neutral-600 group-hover/up:text-neutral-400 transition-colors font-medium">Click to upload</p>
                          <p className="text-[10px] text-neutral-800 mt-0.5">JPG, PNG, WEBP</p>
                        </div>
                      </div>
                    )}
                    <input type="file" ref={fileInputRef} onChange={handlePersonUpload} className="hidden" accept="image/*" />
                  </div>
                  {/* Best-result tips shown when no photo is uploaded yet */}
                  {!personImage && (
                    <div className="bg-amber-500/6 border border-amber-500/15 rounded-xl p-3">
                      <p className="text-[10px] text-amber-400/80 font-semibold mb-1.5 uppercase tracking-wide">For best results</p>
                      <ul className="space-y-0.5 text-[10px] text-neutral-600 leading-relaxed list-disc pl-3.5">
                        <li>Full-body, front-facing photo</li>
                        <li>Neutral background preferred</li>
                        <li>Single person, no cropping</li>
                        <li>Well-lit, ≥ 512 px tall</li>
                      </ul>
                    </div>
                  )}
                  {personImage && (
                    <button
                      onClick={() => { setPersonImage(null); setPersonFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
                      className="w-full text-[11px] text-neutral-700 hover:text-neutral-400 bg-white/3 border border-white/6 py-2 rounded-xl transition-colors flex items-center justify-center gap-1.5"
                    >
                      <X size={10} /> Remove photo
                    </button>
                  )}
                </div>

                {/* Step 2 — Garment */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2.5 mb-1">
                    <div className="w-6 h-6 bg-white/8 border border-white/12 rounded-full flex items-center justify-center text-[11px] font-bold text-neutral-400">2</div>
                    <p className="text-xs font-semibold text-neutral-400 uppercase tracking-widest">Garment</p>
                  </div>
                  <div className="aspect-[3/4] bg-black/30 border border-white/8 rounded-2xl overflow-hidden flex items-center justify-center">
                    {designJob.image ? (
                      <img src={designJob.image} className="w-full h-full object-cover" alt="Garment" />
                    ) : (
                      <div className="text-center space-y-3 p-4">
                        <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center mx-auto">
                          <ImageIcon size={16} className="text-neutral-800" />
                        </div>
                        <p className="text-xs text-neutral-700">No garment selected</p>
                      </div>
                    )}
                  </div>
                  {/* Show a note when the garment is an AI-generated fashion render */}
                  {designJob.garmentSource === 'design' && designJob.image && (
                    <div className="bg-sky-500/6 border border-sky-500/15 rounded-xl p-3">
                      <p className="text-[10px] text-sky-400/80 font-semibold mb-1 uppercase tracking-wide">AI-generated garment</p>
                      <p className="text-[10px] text-neutral-600 leading-relaxed">
                        Best results come from a clean clothing-item photo. For ideal output, pick a garment from the wardrobe or quick-pick grid below.
                      </p>
                    </div>
                  )}
                  <button
                    onClick={() => setActiveTab('runway')}
                    className="w-full text-[11px] text-neutral-700 hover:text-neutral-400 bg-white/3 border border-white/6 py-2 rounded-xl transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Plus size={10} /> Pick from wardrobe
                  </button>
                </div>

                {/* Step 3 — Result */}
                <div className="space-y-3 flex flex-col">
                  <div className="flex items-center gap-2.5 mb-1">
                    <div className={`w-6 h-6 border rounded-full flex items-center justify-center text-[11px] font-bold transition-colors
                      ${tryOnJob.status === 'completed' && tryOnJob.resultImage
                        ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
                        : 'bg-white/8 border-white/12 text-neutral-400'}`}>
                      {tryOnJob.status === 'completed' && tryOnJob.resultImage ? '✓' : '3'}
                    </div>
                    <p className="text-xs font-semibold text-neutral-400 uppercase tracking-widest">Result</p>
                  </div>
                  <div className="flex-1 min-h-[220px] bg-black/30 border border-white/8 rounded-2xl overflow-hidden flex items-center justify-center relative">
                    {tryOnJob.status === 'processing' ? (
                      <div className="text-center space-y-3 p-4">
                        <div className="relative w-10 h-10 mx-auto">
                          <div className="absolute inset-0 rounded-full border border-white/6" />
                          <div className="absolute inset-0 rounded-full border-t border-violet-500 animate-spin" />
                          <div className="absolute inset-2 rounded-full border-t border-indigo-400 animate-spin" style={{ animationDuration: '1.4s', animationDirection: 'reverse' }} />
                        </div>
                        <p className="text-xs text-neutral-400 font-medium">{tryOnJob.statusMsg || 'Processing…'}</p>
                        <div className="w-32 h-1 bg-white/5 rounded-full overflow-hidden mx-auto">
                          <div className="h-full shimmer-bg rounded-full" />
                        </div>
                      </div>
                    ) : tryOnJob.status === 'failed' ? (
                      <div className="text-center space-y-3 p-4">
                        <div className="w-10 h-10 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-center mx-auto">
                          <X size={16} className="text-red-400" />
                        </div>
                        <p className="text-xs text-red-400 font-medium">Try-On Failed</p>
                        <p className="text-[10px] text-neutral-400 leading-relaxed px-2">{tryOnJob.statusMsg}</p>
                      </div>
                    ) : tryOnJob.resultImage ? (
                      <>
                        <img src={tryOnJob.resultImage} className="w-full h-full object-cover" alt="Try-on result" />
                        <button
                          onClick={() => setExpandedImage(tryOnJob.resultImage)}
                          className="absolute bottom-2.5 right-2.5 w-8 h-8 bg-black/60 backdrop-blur rounded-lg text-white border border-white/10 flex items-center justify-center"
                        >
                          <Maximize2 size={12} />
                        </button>
                      </>
                    ) : (
                      <div className="text-center space-y-3 p-4">
                        <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center mx-auto">
                          <User size={16} className="text-neutral-800" />
                        </div>
                        <p className="text-xs text-neutral-700">Result will appear here</p>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleTryOn}
                    disabled={!personFile || !designJob.image || tryOnJob.status === 'processing'}
                    className="w-full bg-white text-black py-3 rounded-xl text-sm font-bold hover:bg-neutral-100 disabled:opacity-25 disabled:cursor-not-allowed active:scale-95 transition-all"
                  >
                    {tryOnJob.status === 'processing'
                      ? <span className="flex items-center justify-center gap-2"><Loader2 size={14} className="animate-spin" /> {tryOnJob.statusMsg || 'Processing…'}</span>
                      : tryOnJob.status === 'failed'
                        ? 'Retry Try-On'
                        : 'Virtual Try-On'}
                  </button>
                </div>
              </div>
            </div>

            {/* ── Quick-Pick Garments ───────────────────────────────────── */}
            <div className="bg-white/2 border border-white/6 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs font-semibold text-neutral-300 uppercase tracking-widest">Quick-Pick Garments</p>
                  <p className="text-[10px] text-neutral-600 mt-0.5">Click any garment to set it as the try-on item</p>
                </div>
                {designJob.image && (
                  <button
                    onClick={() => setDesignJob(prev => ({ ...prev, image: null }))}
                    className="text-[10px] text-neutral-700 hover:text-neutral-400 flex items-center gap-1 transition-colors"
                  >
                    <X size={9} /> Clear
                  </button>
                )}
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
                {ONLINE_GARMENTS.map(g => {
                  const isSelected = designJob.image === g.url;
                  return (
                    <button
                      key={g.id}
                      onClick={() => setDesignJob(prev => ({
                        ...prev,
                        image: g.url,
                        garmentSource: 'online',
                        garmentDescription: g.label,
                      }))}
                      className={`group relative rounded-xl overflow-hidden border transition-all focus:outline-none
                        ${isSelected
                          ? 'border-violet-500/70 ring-2 ring-violet-500/30'
                          : 'border-white/8 hover:border-white/24'}`}
                    >
                      <div className="aspect-[3/4] bg-black/30">
                        <img
                          src={g.url}
                          alt={g.label}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          loading="lazy"
                        />
                      </div>
                      {isSelected && (
                        <div className="absolute top-1.5 right-1.5 w-5 h-5 bg-violet-500 rounded-full flex items-center justify-center shadow-lg">
                          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                            <path d="M2 5l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </div>
                      )}
                      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-1.5 pt-4">
                        <p className="text-[9px] text-white font-medium leading-tight truncate">{g.label}</p>
                        <span className={`inline-block mt-0.5 text-[8px] px-1 py-px rounded border ${CAT_COLORS[g.category] || CAT_COLORS.Casual}`}>
                          {g.category}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

          </div>
        )}

        {/* ══════════════════════════ COLLECTION ══════════════════════════ */}
        {activeTab === 'collection' && (
          <div className="space-y-7 anim-fade-up">

            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Saved Designs</h2>
                <p className="text-xs text-neutral-600 mt-1">
                  {savedDesigns.length} design{savedDesigns.length !== 1 ? 's' : ''} saved locally
                </p>
              </div>
              <button
                onClick={() => setActiveTab('design')}
                className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white bg-white/4 border border-white/8 hover:border-white/16 px-3.5 py-2 rounded-xl transition-all"
              >
                <Plus size={11} /> New Design
              </button>
            </div>

            {savedDesigns.length === 0 ? (
              <div className="bg-white/2 border border-white/5 rounded-2xl py-20 text-center">
                <div className="w-12 h-12 bg-white/4 border border-white/8 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Layers size={20} className="text-neutral-700" />
                </div>
                <p className="text-sm text-neutral-500 font-medium mb-1">Your collection is empty</p>
                <p className="text-xs text-neutral-700 mb-5">Generate a design and save it to build your collection</p>
                <button
                  onClick={() => setActiveTab('design')}
                  className="inline-flex items-center gap-2 text-xs text-violet-400 bg-violet-400/8 border border-violet-400/20 px-5 py-2.5 rounded-xl hover:bg-violet-400/14 transition-colors font-semibold"
                >
                  <Sparkles size={11} /> Open Studio
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                {savedDesigns.map(design => (
                  <div
                    key={design.id}
                    className="bg-white/3 border border-white/7 rounded-2xl overflow-hidden flex flex-col group card-hover"
                  >
                    {/* Image */}
                    <div className="aspect-[3/4] overflow-hidden bg-neutral-950 relative">
                      <img
                        src={design.image}
                        className="w-full h-full object-cover group-hover:scale-[1.04] transition-transform duration-500"
                        alt="Saved design"
                      />
                      <button
                        onClick={() => setExpandedImage(design.image)}
                        className="absolute top-2.5 right-2.5 w-8 h-8 bg-black/60 backdrop-blur rounded-lg text-white/60 hover:text-white border border-white/10 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center"
                      >
                        <Maximize2 size={12} />
                      </button>
                    </div>

                    {/* Info */}
                    <div className="p-4 flex flex-col gap-3 flex-1">
                      <p className="text-xs text-neutral-400 line-clamp-2 leading-relaxed flex-1">{design.prompt}</p>
                      {design.spec?.colors?.length > 0 && (
                        <div className="flex items-center gap-1.5">
                          {design.spec.colors.slice(0, 5).map(c => (
                            <div key={c} className="w-3.5 h-3.5 rounded-full ring-1 ring-black/40" style={{ backgroundColor: c }} />
                          ))}
                          {design.spec.sustainability_score && (
                            <span className="ml-auto text-[10px] text-emerald-500 font-semibold">{design.spec.sustainability_score}/100</span>
                          )}
                        </div>
                      )}
                      <div className="flex items-center justify-between pt-2.5 border-t border-white/5">
                        <button
                          onClick={() => setSavedDesigns(StorageService.toggleTrack(design.id))}
                          className={`flex items-center gap-1.5 text-[10px] font-semibold transition-colors
                            ${design.isTracking ? 'text-emerald-400' : 'text-neutral-700 hover:text-neutral-400'}`}
                        >
                          {design.isTracking ? <BellRing size={11} /> : <Bell size={11} />}
                          {design.isTracking ? 'Tracking' : 'Track'}
                        </button>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleGenerateDesign(design.prompt)}
                            title="Remix"
                            className="w-7 h-7 text-neutral-700 hover:text-violet-400 hover:bg-violet-400/10 rounded-lg flex items-center justify-center transition-all"
                          >
                            <RefreshCw size={12} />
                          </button>
                          <button
                            onClick={() => { StorageService.deleteDesign(design.id); setSavedDesigns(StorageService.getCollections()); }}
                            title="Delete"
                            className="w-7 h-7 text-neutral-800 hover:text-red-400 hover:bg-red-400/10 rounded-lg flex items-center justify-center transition-all"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </main>

      {/* ── FOOTER ────────────────────────────────────────────────── */}
      <footer className="border-t border-white/5 mt-4">
        <div className="max-w-7xl mx-auto px-5 py-5 flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Brand */}
          <div className="flex items-center gap-2 select-none">
            <div className="w-5 h-5 bg-white rounded-md flex items-center justify-center">
              <Scissors size={10} className="text-black" />
            </div>
            <span className="text-xs font-semibold text-neutral-400 tracking-tight">Studio AI</span>
          </div>

          {/* Credit */}
          <p className="text-xs text-neutral-700 text-center">
            Designed &amp; built by{' '}
            <span className="text-neutral-300 font-semibold">Piyush Ramteke</span>
            {' '}·{' '}
            <span className="text-neutral-600">IBM Internship 2026</span>
          </p>

          {/* Badge */}
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] text-neutral-700 font-medium">AI Fashion Studio</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
