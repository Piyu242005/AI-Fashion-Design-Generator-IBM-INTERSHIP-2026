import React, { useState, useRef, useEffect } from 'react';

/* ─── SAMPLE WARDROBE IMPORTS ─────────────────────────────────────── */
import imgBeigeJacket      from '../SAMPLES CLOTHES/beige-moto-jacket-navy-dress.jpg';
import imgBlackCropMaxi    from '../SAMPLES CLOTHES/black-crop-top-maxi-skirt.jpg';
import imgBlackCropSkirt   from '../SAMPLES CLOTHES/black-crop-top-skirt-set.jpg';
import imgBlueHoodie       from '../SAMPLES CLOTHES/blue-oversized-hoodie.jpg';
import imgCreamHoodie      from '../SAMPLES CLOTHES/cream-oversized-hoodie.jpg';
import imgDenimShirt       from '../SAMPLES CLOTHES/denim-shirt-beige-trousers-outfit.jpg';
import imgMensBlackHoodie  from '../SAMPLES CLOTHES/mens-black-hoodie.jpg';
import imgGeometricShirt   from '../SAMPLES CLOTHES/mens-geometric-print-shirt.jpg';
import imgWhiteTshirt      from '../SAMPLES CLOTHES/mens-white-tshirt-jeans.jpg';
import imgPinkSweater      from '../SAMPLES CLOTHES/pink-sweater-navy-jeans-outfit.jpg';
import imgTealBlazer       from '../SAMPLES CLOTHES/teal-blazer-grey-jeans.jpg';
import imgTealTrio         from '../SAMPLES CLOTHES/teal-khaki-black-dresses-trio.jpg';
import imgVintageDenim     from '../SAMPLES CLOTHES/vintage-denim-jacket.jpg';
import imgWhiteKnit        from '../SAMPLES CLOTHES/white-knit-flare-jeans-outfit.jpg';
import imgWhiteShirt       from '../SAMPLES CLOTHES/white-shirt-long-sleeve.webp';
import imgYellowTop        from '../SAMPLES CLOTHES/yellow-top-brown-culottes-outfit.jpg';

import {
  Sparkles, Image as ImageIcon, Loader2, Download,
  Scissors, ShoppingBag, User, Upload, Layers, Trash2,
  Maximize2, RefreshCw, X, Camera, Palette, Leaf, FileText,
  Bell, BellRing, Activity, Wand2, ChevronRight, Star,
  TrendingUp, Zap, ArrowRight, Cpu, ChevronDown
} from 'lucide-react';

/* ─── CONFIG ──────────────────────────────────────────────────────── */
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "";
const GEMINI_MODEL   = import.meta.env.VITE_GEMINI_MODEL   || "gemini-2.5-flash";
const BACKEND_URL    = import.meta.env.VITE_BACKEND_URL    || "http://localhost:8000";

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
    if (!GEMINI_API_KEY) return this.mockSpec(prompt);
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;
      const payload = {
        contents: [{ parts: [{ text: `Extract fashion details to JSON: ${prompt}. Schema: {"category":"","fabric":"","colors":["hex"],"sustainability_score":0,"budget":{"maximum":0}}` }] }],
        generationConfig: { responseMimeType: "application/json" }
      };
      const res  = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      return JSON.parse(cleanJSON(data.candidates[0].content.parts[0].text));
    } catch { return this.mockSpec(prompt); }
  },
  mockSpec: (prompt) => ({
    category: prompt.toLowerCase().includes("kurta") ? "Kurta" : prompt.toLowerCase().includes("saree") ? "Saree" : "Jacket",
    fabric: "Organic Cotton",
    colors: ["#0f172a", "#334155", "#94a3b8"],
    sustainability_score: 85,
    budget: { maximum: 2999 },
    optimized_image_prompt: prompt
  })
};

/* ─── IMAGE MODELS CATALOGUE ──────────────────────────────────────── */
export const IMAGE_MODELS = [
  {
    id: "@cf/black-forest-labs/flux-1-schnell",
    label: "FLUX.1 Schnell",
    provider: "Cloudflare",
    badge: "Fast",
    badgeColor: "text-sky-400 bg-sky-400/10 border-sky-400/20",
    description: "Best quality/speed for fashion renders",
    default: true,
  },
  {
    id: "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    label: "SDXL Base 1.0",
    provider: "Cloudflare",
    badge: "Detailed",
    badgeColor: "text-violet-400 bg-violet-400/10 border-violet-400/20",
    description: "Higher detail, slightly slower",
    default: false,
  },
  {
    id: "@cf/lykon/dreamshaper-8-lcm",
    label: "DreamShaper 8",
    provider: "Cloudflare",
    badge: "Artistic",
    badgeColor: "text-rose-400 bg-rose-400/10 border-rose-400/20",
    description: "Painterly, creative fashion illustrations",
    default: false,
  },
  {
    id: "@cf/bytedance/stable-diffusion-xl-lightning",
    label: "SDXL Lightning",
    provider: "Cloudflare",
    badge: "Fastest",
    badgeColor: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    description: "Ultra-fast 4-step generation",
    default: false,
  },
];

const FALLBACK_IMAGE = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80";

const ImageGenerationService = {
  /**
   * Primary route  : POST /api/design          → Cloudflare (model selectable)
   * Fallback route : POST /api/generate-image  → HuggingFace FLUX.1-schnell
   * Both routes live in the FastAPI backend — the token NEVER touches the browser.
   */
  async generate(optimizedPrompt, modelId = null) {
    // ── 1. Try Cloudflare via /api/design ──────────────────────────────
    try {
      const body = { prompt: optimizedPrompt };
      if (modelId) body.model = modelId;
      const res = await fetch(`${BACKEND_URL}/api/design`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.image) return data.image;
      } else {
        const err = await res.json().catch(() => ({}));
        // 503 = backend not configured → fall through to HF route
        if (res.status !== 503) {
          console.warn('[ImageGen] Cloudflare error:', err?.error?.code);
        }
      }
    } catch (e) {
      console.warn('[ImageGen] /api/design unreachable, trying HF fallback:', e.message);
    }

    // ── 2. Fallback: HuggingFace /api/generate-image ──────────────────
    try {
      const res = await fetch(`${BACKEND_URL}/api/generate-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: optimizedPrompt }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.image_base64) return data.image_base64;
      } else {
        const err = await res.json().catch(() => ({}));
        if (err?.detail?.fallback_url) return err.detail.fallback_url;
      }
    } catch (e) {
      console.warn('[ImageGen] /api/generate-image also unreachable:', e.message);
    }

    // ── 3. Final fallback: static placeholder ─────────────────────────
    return FALLBACK_IMAGE;
  }
};

const ProductSearchService = {
  async searchSimilarProducts(spec) {
    await new Promise(r => setTimeout(r, 400));
    return [
      { name: "Minimalist " + spec.category, price: 1499, platform: "Myntra",   similarity_score: 92, tag: "Best Match" },
      { name: "Premium " + spec.fabric + " Blend", price: 2199, platform: "Ajio",     similarity_score: 88, tag: "Popular" },
      { name: "Urban Streetwear Concept",     price: 2899, platform: "Tata CLiQ", similarity_score: 85, tag: "Trending" }
    ];
  }
};

const VirtualTryOnService = {
  async processTryOn(personImage, garmentImage) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const canvas  = document.createElement('canvas');
        const scratch = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const pImg = new Image(), gImg = new Image();
        pImg.crossOrigin = gImg.crossOrigin = "anonymous";

        pImg.onload = () => {
          const W = pImg.width, H = pImg.height;
          canvas.width  = scratch.width  = W;
          canvas.height = scratch.height = H;

          gImg.onload = () => {
            // ── 1. Draw full person as base ──────────────────────────
            ctx.drawImage(pImg, 0, 0, W, H);

            // ── 2. Build garment layer on scratch canvas ─────────────
            //    Scale garment to cover the torso region (top 20% → 85%)
            const sc  = scratch.getContext('2d');
            const torsoTop    = H * 0.18;
            const torsoHeight = H * 0.67;
            const gAspect     = gImg.width / gImg.height;
            const gW          = W;
            const gH          = gW / gAspect;
            // centre the garment and offset so it starts at the shoulder
            const gX = 0;
            const gY = torsoTop - (gH - torsoHeight) * 0.15;

            sc.drawImage(gImg, gX, gY, gW, gH);

            // ── 3. Blend garment onto person using 'multiply' ────────
            //    This darkens person's clothing area with the garment colour,
            //    giving a natural colour-replacement look without a hard edge.
            ctx.save();
            ctx.globalCompositeOperation = 'multiply';
            ctx.globalAlpha = 0.82;
            ctx.drawImage(scratch, 0, 0);
            ctx.restore();

            // ── 4. Restore person's face/head cleanly on top ─────────
            //    Re-draw the top ~22% of the person over the garment layer
            //    so the face is never obscured.
            const headH = H * 0.22;
            ctx.drawImage(pImg, 0, 0, W, headH, 0, 0, W, headH);

            // ── 5. Subtle vignette to unify the composite ────────────
            const vignette = ctx.createRadialGradient(W/2, H/2, H*0.3, W/2, H/2, H*0.85);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.18)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);

            resolve({ resultImage: canvas.toDataURL('image/jpeg', 0.92) });
          };
          gImg.src = garmentImage;
        };
        pImg.src = personImage;
      }, 2500);
    });
  }
};

/* ─── SAMPLE WARDROBE ─────────────────────────────────────────────── */
const sampleWardrobe = [
  { id: 1,  label: "Beige Moto Jacket",         image: imgBeigeJacket,     category: "Jacket" },
  { id: 2,  label: "Black Crop Top & Maxi",     image: imgBlackCropMaxi,   category: "Set" },
  { id: 3,  label: "Black Crop & Skirt Set",    image: imgBlackCropSkirt,  category: "Set" },
  { id: 4,  label: "Blue Oversized Hoodie",     image: imgBlueHoodie,      category: "Casual" },
  { id: 5,  label: "Cream Oversized Hoodie",    image: imgCreamHoodie,     category: "Casual" },
  { id: 6,  label: "Denim Shirt & Trousers",    image: imgDenimShirt,      category: "Casual" },
  { id: 7,  label: "Men's Black Hoodie",        image: imgMensBlackHoodie, category: "Men" },
  { id: 8,  label: "Geometric Print Shirt",     image: imgGeometricShirt,  category: "Men" },
  { id: 9,  label: "White T-Shirt & Jeans",     image: imgWhiteTshirt,     category: "Men" },
  { id: 10, label: "Pink Sweater & Navy Jeans", image: imgPinkSweater,     category: "Casual" },
  { id: 11, label: "Teal Blazer & Grey Jeans",  image: imgTealBlazer,      category: "Formal" },
  { id: 12, label: "Teal, Khaki & Black Trio",  image: imgTealTrio,        category: "Dress" },
  { id: 13, label: "Vintage Denim Jacket",      image: imgVintageDenim,    category: "Jacket" },
  { id: 14, label: "White Knit & Flare Jeans",  image: imgWhiteKnit,       category: "Casual" },
  { id: 15, label: "White Long Sleeve Shirt",   image: imgWhiteShirt,      category: "Formal" },
  { id: 16, label: "Yellow Top & Brown Culotte",image: imgYellowTop,       category: "Casual" },
];

const WARDROBE_CATEGORY_COLORS = {
  "Jacket":  "bg-amber-500/15 text-amber-400 border-amber-500/30",
  "Set":     "bg-violet-500/15 text-violet-400 border-violet-500/30",
  "Casual":  "bg-sky-500/15 text-sky-400 border-sky-500/30",
  "Men":     "bg-neutral-500/15 text-neutral-400 border-neutral-500/30",
  "Formal":  "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  "Dress":   "bg-rose-500/15 text-rose-400 border-rose-500/30",
};

/* ─── RUNWAY DATA ─────────────────────────────────────────────────── */
const runwayData = [
  {
    id: 1,
    prompt: "Cyberpunk streetwear jacket with neon accents",
    image: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&q=80",
    tag: "Trending",
    designer: "Studio AI",
    likes: 284
  },
  {
    id: 2,
    prompt: "Indo-western fusion lehenga, minimalist beige",
    image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80",
    tag: "Featured",
    designer: "Runway AI",
    likes: 521
  },
  {
    id: 3,
    prompt: "Sustainable bamboo fabric summer dress",
    image: "https://images.unsplash.com/photo-1515347619362-e5fdffdc8fb8?w=800&q=80",
    tag: "Eco Pick",
    designer: "Green Studio",
    likes: 193
  },
  {
    id: 4,
    prompt: "Royal Rajasthani bandhani kurta in indigo with gold block print",
    image: "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=800&q=80",
    tag: "New",
    designer: "Heritage AI",
    likes: 412
  },
  {
    id: 5,
    prompt: "Oversized linen co-ord set, soft terracotta tones",
    image: "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800&q=80",
    tag: "Minimal",
    designer: "Form Studio",
    likes: 337
  },
  {
    id: 6,
    prompt: "Contemporary silk saree with geometric motif border",
    image: "https://images.unsplash.com/photo-1617137968427-85924c800a22?w=800&q=80",
    tag: "Classic",
    designer: "Loom AI",
    likes: 609
  }
];

const TAG_COLORS = {
  "Trending": "bg-rose-500/15 text-rose-400 border-rose-500/30",
  "Featured": "bg-violet-500/15 text-violet-400 border-violet-500/30",
  "Eco Pick": "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  "New":      "bg-sky-500/15 text-sky-400 border-sky-500/30",
  "Minimal":  "bg-neutral-500/15 text-neutral-400 border-neutral-500/30",
  "Classic":  "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

/* ─── STATS TICKER ────────────────────────────────────────────────── */
const stats = [
  { label: "Designs Generated", value: "48K+" },
  { label: "Active Designers", value: "12K" },
  { label: "Avg. Eco Score", value: "87/100" },
  { label: "Indian Styles", value: "200+" },
];

/* ════════════════════════════════════════════════════════════════════
   MAIN APP
═══════════════════════════════════════════════════════════════════ */
export default function App() {
  const [activeTab, setActiveTab]   = useState('runway');
  const [prompt, setPrompt]         = useState("");
  const [selectedModel, setSelectedModel] = useState(IMAGE_MODELS.find(m => m.default).id);
  const [modelDropOpen, setModelDropOpen] = useState(false);
  const [designJob, setDesignJob]   = useState({ status: 'idle', spec: null, image: null, products: [] });
  const [expandedImage, setExpandedImage] = useState(null);
  const [showTechPack, setShowTechPack]   = useState(false);
  const [personImage, setPersonImage]     = useState(null);
  const [tryOnJob, setTryOnJob]           = useState({ status: 'idle', resultImage: null });
  const [bodyAnalysis, setBodyAnalysis]   = useState(null);
  const [savedDesigns, setSavedDesigns]   = useState([]);
  const [savePulse, setSavePulse]         = useState(false);
  const [wardrobeFilter, setWardrobeFilter] = useState('All');
  const fileInputRef = useRef(null);
  const modelDropRef = useRef(null);

  // Close model dropdown when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (modelDropRef.current && !modelDropRef.current.contains(e.target))
        setModelDropOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  useEffect(() => { setSavedDesigns(StorageService.getCollections()); }, []);

  const handleGenerateDesign = async (overridePrompt = null) => {
    const targetPrompt = overridePrompt || prompt;
    if (!targetPrompt.trim()) return;
    setPrompt(targetPrompt);
    if (activeTab !== 'design') setActiveTab('design');
    setDesignJob({ status: 'processing', spec: null, image: null, products: [] });
    try {
      const spec = await FashionIntelligenceService.extractSpecification(targetPrompt);
      const [image, products] = await Promise.all([
        ImageGenerationService.generate(spec.optimized_image_prompt || targetPrompt, selectedModel),
        ProductSearchService.searchSimilarProducts(spec)
      ]);
      setDesignJob({ status: 'completed', spec, image, products, prompt: targetPrompt });
    } catch {
      setDesignJob({ status: 'failed', spec: null, image: null, products: [] });
    }
  };

  const handleSaveDesign = () => {
    StorageService.saveDesign({ image: designJob.image, prompt: designJob.prompt, spec: designJob.spec });
    setSavedDesigns(StorageService.getCollections());
    setSavePulse(true);
    setTimeout(() => setSavePulse(false), 1200);
  };

  const handlePersonUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setPersonImage(ev.target.result);
      setBodyAnalysis(null);
      setTimeout(() => setBodyAnalysis({ shape: 'Athletic / Rectangle', match: 92, tips: 'Structured shoulders and a cinched waist will complement your proportions perfectly.' }), 2200);
    };
    reader.readAsDataURL(file);
  };

  const handleTryOn = async () => {
    if (!personImage || !designJob.image) return;
    setTryOnJob({ status: 'processing', resultImage: null });
    const result = await VirtualTryOnService.processTryOn(personImage, designJob.image);
    setTryOnJob({ status: 'completed', resultImage: result.resultImage });
  };

  const tabs = [
    { id: 'runway',     label: 'Runway',               icon: Activity  },
    { id: 'design',     label: 'Studio',               icon: Sparkles  },
    { id: 'tryon',      label: 'Try-On',               icon: User      },
    { id: 'collection', label: `Saved · ${savedDesigns.length}`, icon: Layers },
  ];

  /* ── RENDER ────────────────────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-[#080808] text-neutral-100 font-sans antialiased selection:bg-violet-900/40">

      {/* ── LIGHTBOX ─────────────────────────────────────────────── */}
      {expandedImage && (
        <div
          className="fixed inset-0 z-[200] bg-black/96 backdrop-blur-xl flex items-center justify-center p-4"
          onClick={() => setExpandedImage(null)}
        >
          <button className="absolute top-5 right-5 bg-white/10 hover:bg-white/20 text-white p-2.5 rounded-full transition-colors border border-white/10">
            <X size={20} />
          </button>
          <img
            src={expandedImage} alt="Expanded"
            className="max-w-[90vw] max-h-[90vh] rounded-2xl object-contain shadow-2xl ring-1 ring-white/10"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}

      {/* ── TECH PACK MODAL ──────────────────────────────────────── */}
      {showTechPack && designJob.spec && (
        <div className="fixed inset-0 z-[200] bg-black/85 backdrop-blur-lg flex items-center justify-center p-4">
          <div className="bg-[#0e0e0e] border border-neutral-800/80 rounded-3xl w-full max-w-xl overflow-hidden shadow-2xl ring-1 ring-white/5">
            <div className="flex justify-between items-center px-6 py-4 border-b border-neutral-800/60 bg-[#0a0a0a]">
              <h2 className="font-semibold text-sm flex items-center gap-2 text-neutral-200">
                <FileText size={15} className="text-violet-400" /> Manufacturing Tech Pack
              </h2>
              <button onClick={() => setShowTechPack(false)} className="text-neutral-500 hover:text-white transition-colors p-1">
                <X size={18} />
              </button>
            </div>
            <div className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Primary Fabric",    value: designJob.spec.fabric || "Unknown" },
                  { label: "Category",          value: designJob.spec.category || "Apparel" },
                  { label: "Color Codes (HEX)", value: designJob.spec.colors?.join(", ") || "N/A" },
                  { label: "Est. Cost Price",   value: `₹${(designJob.spec.budget?.maximum * 0.4 || 0).toFixed(0)}` },
                ].map(f => (
                  <div key={f.label} className="bg-neutral-900/60 border border-neutral-800/60 p-3 rounded-xl">
                    <span className="text-neutral-500 text-[10px] uppercase tracking-wider block mb-1">{f.label}</span>
                    <span className="text-neutral-200 text-sm font-medium">{f.value}</span>
                  </div>
                ))}
              </div>
              <div className="bg-neutral-900/40 border border-neutral-800/50 p-4 rounded-xl">
                <h4 className="text-xs font-semibold text-neutral-300 mb-2 uppercase tracking-wider">Construction Notes</h4>
                <ul className="space-y-1.5 text-xs text-neutral-500 list-disc pl-4">
                  <li>Standard 1.5 cm seam allowance on all panels.</li>
                  <li>Use eco-friendly dyes — target Eco Score: <span className="text-emerald-400">{designJob.spec.sustainability_score || 80}/100</span>.</li>
                  <li className="text-neutral-600 italic line-clamp-1">Derived from: "{designJob.prompt}"</li>
                </ul>
              </div>
              <button
                onClick={() => setShowTechPack(false)}
                className="w-full bg-white text-black py-2.5 rounded-xl text-sm font-semibold hover:bg-neutral-100 transition-colors"
              >
                Download PDF <span className="text-neutral-500 font-normal">(Simulated)</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── NAV ──────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 border-b border-neutral-900/80 bg-[#080808]/90 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-5 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="bg-white text-black p-1.5 rounded-lg">
              <Scissors size={15} />
            </div>
            <span className="font-semibold text-[15px] tracking-tight hidden sm:block">AI Fashion Studio</span>
            <span className="ml-1 text-[10px] font-medium text-violet-400 bg-violet-400/10 border border-violet-400/20 px-1.5 py-0.5 rounded-md hidden sm:inline">BETA</span>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-0.5 bg-neutral-900/60 border border-neutral-800/60 p-1 rounded-xl">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-3.5 py-1.5 rounded-lg text-[13px] font-medium flex items-center gap-1.5 transition-all duration-200 whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'bg-neutral-800 text-white shadow-sm'
                    : 'text-neutral-500 hover:text-neutral-300 hover:bg-neutral-800/40'}`}
              >
                <tab.icon size={13} />
                {tab.label}
                {tab.id === 'collection' && savedDesigns.length > 0 && activeTab !== 'collection' && (
                  <span className="absolute -top-1 -right-1 bg-violet-500 text-white text-[9px] font-bold rounded-full w-3.5 h-3.5 flex items-center justify-center">
                    {savedDesigns.length > 9 ? '9+' : savedDesigns.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* ── MAIN ─────────────────────────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-5 py-8">

        {/* ════════════ RUNWAY ════════════ */}
        {activeTab === 'runway' && (
          <div className="space-y-10">

            {/* Hero */}
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-neutral-900 via-[#0e0e0e] to-neutral-900 border border-neutral-800/60 p-10 md:p-14 text-center">
              {/* Subtle grid texture */}
              <div className="absolute inset-0 opacity-[0.03]"
                style={{ backgroundImage: 'linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)', backgroundSize: '40px 40px' }} />
              <div className="relative z-10">
                <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium px-3 py-1.5 rounded-full mb-5">
                  <Zap size={11} /> AI-Powered Fashion Intelligence
                </div>
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight tracking-tight">
                  Design. Try. Wear.
                </h1>
                <p className="text-neutral-400 text-base max-w-lg mx-auto mb-8 leading-relaxed">
                  Describe any outfit in plain language — our AI renders it, suggests real alternatives, and lets you try it on.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    onClick={() => setActiveTab('design')}
                    className="inline-flex items-center justify-center gap-2 bg-white text-black px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-neutral-100 transition-colors"
                  >
                    <Wand2 size={15} /> Open Studio <ArrowRight size={13} />
                  </button>
                  <button
                    onClick={() => document.getElementById('runway-grid')?.scrollIntoView({ behavior: 'smooth' })}
                    className="inline-flex items-center justify-center gap-2 bg-neutral-800/60 text-neutral-300 border border-neutral-700/60 px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-neutral-800 transition-colors"
                  >
                    Browse Inspiration
                  </button>
                </div>
              </div>
            </div>

            {/* Stats Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {stats.map(s => (
                <div key={s.label} className="bg-neutral-900/50 border border-neutral-800/50 rounded-2xl p-4 text-center">
                  <div className="text-xl font-bold text-white mb-0.5">{s.value}</div>
                  <div className="text-[11px] text-neutral-500">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Runway Grid */}
            <div id="runway-grid">
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-base font-semibold text-neutral-200 flex items-center gap-2">
                  <TrendingUp size={15} className="text-violet-400" /> Trending Concepts
                </h2>
                <span className="text-xs text-neutral-600">Click any card to remix in Studio →</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {runwayData.map((item) => (
                  <div
                    key={item.id}
                    className="group relative bg-neutral-900/40 border border-neutral-800/50 rounded-2xl overflow-hidden hover:border-neutral-700/80 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/40"
                  >
                    {/* Image */}
                    <div className="h-72 w-full overflow-hidden bg-neutral-950">
                      <img
                        src={item.image}
                        alt={item.prompt}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                        onError={e => { e.target.src = FALLBACK_IMAGE; }}
                      />
                    </div>

                    {/* Tag */}
                    <div className="absolute top-3 left-3">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${TAG_COLORS[item.tag] || TAG_COLORS["Minimal"]}`}>
                        {item.tag}
                      </span>
                    </div>

                    {/* Overlay on hover */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80 group-hover:opacity-100 transition-opacity" />

                    {/* Bottom content */}
                    <div className="absolute bottom-0 inset-x-0 p-4">
                      <div className="flex items-center gap-1.5 mb-2">
                        <div className="w-4 h-4 rounded-full bg-neutral-700 flex items-center justify-center">
                          <User size={8} className="text-neutral-300" />
                        </div>
                        <span className="text-[10px] text-neutral-400">{item.designer}</span>
                        <span className="ml-auto text-[10px] text-neutral-500 flex items-center gap-0.5">
                          <Star size={9} className="text-amber-400 fill-amber-400" /> {item.likes}
                        </span>
                      </div>
                      <p className="text-xs text-neutral-200 leading-snug mb-3 line-clamp-2">{item.prompt}</p>
                      <button
                        onClick={() => handleGenerateDesign(item.prompt)}
                        className="w-full bg-white/15 backdrop-blur-md text-white border border-white/20 py-2 rounded-xl text-xs font-semibold hover:bg-white hover:text-black transition-all duration-200 flex items-center justify-center gap-1.5"
                      >
                        <Sparkles size={11} /> Remix in Studio
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Sample Wardrobe */}
            <div id="sample-wardrobe">
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-base font-semibold text-neutral-200 flex items-center gap-2">
                  <Layers size={15} className="text-violet-400" /> Sample Wardrobe
                </h2>
                <span className="text-xs text-neutral-600">{sampleWardrobe.length} pieces · click to try on →</span>
              </div>

              {/* Category filter pills */}
              <div className="flex flex-wrap gap-2 mb-5">
                {['All', ...Array.from(new Set(sampleWardrobe.map(w => w.category)))].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setWardrobeFilter(cat)}
                    className={`text-[11px] font-medium px-3 py-1 rounded-full border transition-all
                      ${wardrobeFilter === cat
                        ? 'bg-white text-black border-white'
                        : 'bg-neutral-800/50 text-neutral-400 border-neutral-700/50 hover:text-white hover:border-neutral-600'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                {sampleWardrobe
                  .filter(w => wardrobeFilter === 'All' || w.category === wardrobeFilter)
                  .map(item => (
                    <div
                      key={item.id}
                      className="group relative bg-neutral-900/40 border border-neutral-800/50 rounded-2xl overflow-hidden hover:border-neutral-700/80 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/40 cursor-pointer"
                      onClick={() => { setDesignJob(prev => ({ ...prev, image: item.image })); setActiveTab('tryon'); }}
                    >
                      {/* Image */}
                      <div className="h-52 w-full overflow-hidden bg-neutral-950">
                        <img
                          src={item.image}
                          alt={item.label}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                          onError={e => { e.target.src = FALLBACK_IMAGE; }}
                        />
                      </div>

                      {/* Category badge */}
                      <div className="absolute top-2.5 left-2.5">
                        <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded-full border ${WARDROBE_CATEGORY_COLORS[item.category] || 'bg-neutral-500/15 text-neutral-400 border-neutral-500/30'}`}>
                          {item.category}
                        </span>
                      </div>

                      {/* Overlay */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                      {/* Bottom label + CTA */}
                      <div className="absolute bottom-0 inset-x-0 p-3 translate-y-2 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-200">
                        <p className="text-[11px] text-white font-medium leading-snug mb-2 line-clamp-1">{item.label}</p>
                        <button className="w-full bg-white/15 backdrop-blur-md text-white border border-white/20 py-1.5 rounded-lg text-[10px] font-semibold hover:bg-white hover:text-black transition-all flex items-center justify-center gap-1">
                          <User size={9} /> Try On
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

          </div>
        )}

        {/* ════════════ DESIGN STUDIO ════════════ */}
        {activeTab === 'design' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* Left Panel */}
            <aside className="lg:col-span-4 xl:col-span-3">
              <div className="sticky top-20 bg-neutral-900/40 border border-neutral-800/50 rounded-2xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
                    <Wand2 size={14} className="text-violet-400" /> Design Prompt
                  </h2>
                  <button
                    onClick={() => setPrompt("Reverse Engineered: A navy blue velvet blazer with intricate gold zari embroidery on the lapel, formal wear, Indian style.")}
                    className="flex items-center gap-1 text-[11px] text-neutral-500 hover:text-neutral-300 bg-neutral-800/60 border border-neutral-700/50 px-2 py-1 rounded-lg transition-colors"
                  >
                    <Camera size={11} /> Sample prompt
                  </button>
                </div>

                <form onSubmit={e => { e.preventDefault(); handleGenerateDesign(); }} className="space-y-3">
                  <textarea
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    placeholder="e.g. A minimalist black cotton kurta with subtle white embroidery under ₹3000..."
                    className="w-full h-32 p-3.5 bg-[#080808] border border-neutral-800/80 rounded-xl resize-none focus:outline-none focus:border-neutral-600 text-sm text-neutral-300 placeholder:text-neutral-700 transition-colors leading-relaxed"
                    required
                  />

                  {/* ── Model Selector ───────────────────────────────── */}
                  <div ref={modelDropRef} className="relative">
                    <p className="text-[10px] text-neutral-600 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <Cpu size={9} /> AI Model
                    </p>
                    <button
                      type="button"
                      onClick={() => setModelDropOpen(o => !o)}
                      className="w-full flex items-center justify-between bg-[#080808] border border-neutral-800/80 hover:border-neutral-600 rounded-xl px-3 py-2.5 transition-colors group"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        {(() => {
                          const m = IMAGE_MODELS.find(m => m.id === selectedModel);
                          return (
                            <>
                              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border shrink-0 ${m?.badgeColor}`}>{m?.badge}</span>
                              <span className="text-sm text-neutral-200 font-medium truncate">{m?.label}</span>
                              <span className="text-[10px] text-neutral-600 shrink-0">{m?.provider}</span>
                            </>
                          );
                        })()}
                      </div>
                      <ChevronDown size={13} className={`text-neutral-500 transition-transform shrink-0 ml-1 ${modelDropOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown */}
                    {modelDropOpen && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-[#0e0e0e] border border-neutral-800/80 rounded-xl overflow-hidden shadow-2xl z-50 ring-1 ring-white/5">
                        {IMAGE_MODELS.map(m => (
                          <button
                            key={m.id}
                            type="button"
                            onClick={() => { setSelectedModel(m.id); setModelDropOpen(false); }}
                            className={`w-full flex items-start gap-3 px-3.5 py-3 text-left hover:bg-neutral-800/60 transition-colors border-b border-neutral-800/40 last:border-0
                              ${selectedModel === m.id ? 'bg-neutral-800/40' : ''}`}
                          >
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-sm text-neutral-200 font-medium">{m.label}</span>
                                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${m.badgeColor}`}>{m.badge}</span>
                              </div>
                              <p className="text-[11px] text-neutral-600 leading-snug">{m.description}</p>
                            </div>
                            {selectedModel === m.id && (
                              <div className="w-1.5 h-1.5 rounded-full bg-violet-400 mt-1.5 shrink-0" />
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={designJob.status === 'processing'}
                    className="w-full bg-white text-black py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 hover:bg-neutral-100 disabled:opacity-40 transition-all"
                  >
                    {designJob.status === 'processing'
                      ? <><Loader2 size={15} className="animate-spin" /> Rendering…</>
                      : <><Sparkles size={15} /> Generate Design</>}
                  </button>
                </form>

                {/* Quick prompts */}
                <div>
                  <p className="text-[10px] text-neutral-600 uppercase tracking-wider mb-2">Quick Styles</p>
                  <div className="flex flex-wrap gap-1.5">
                    {["Saree", "Kurta", "Blazer", "Co-ord", "Lehenga"].map(style => (
                      <button
                        key={style}
                        onClick={() => setPrompt(`A premium ${style.toLowerCase()} with contemporary design`)}
                        className="text-[11px] px-2.5 py-1 bg-neutral-800/60 border border-neutral-700/40 text-neutral-400 rounded-lg hover:text-white hover:border-neutral-600 transition-colors"
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </aside>

            {/* Right: Output */}
            <section className="lg:col-span-8 xl:col-span-9">
              {designJob.status === 'completed' && designJob.image ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                  {/* Generated Concept */}
                  <div className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl overflow-hidden group relative flex flex-col">
                    {/* Hover actions */}
                    <div className="absolute top-3 right-3 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                      {[
                        { icon: RefreshCw, title: "Regenerate", action: () => handleGenerateDesign() },
                        { icon: Download,  title: "Download",   action: () => { const a = document.createElement('a'); a.href = designJob.image; a.download = 'design.png'; a.click(); } },
                        { icon: Maximize2, title: "Expand",     action: () => setExpandedImage(designJob.image) },
                      ].map(({ icon: Icon, title, action }) => (
                        <button
                          key={title}
                          onClick={action}
                          title={title}
                          className="bg-black/60 backdrop-blur-md p-2 rounded-lg text-white hover:bg-black/80 border border-white/10 transition-colors"
                        >
                          <Icon size={14} />
                        </button>
                      ))}
                    </div>

                    {/* Image */}
                    <div className="h-80 w-full bg-neutral-950 overflow-hidden">
                      <img src={designJob.image} alt="Generated Design" className="w-full h-full object-cover" />
                    </div>

                    {/* Spec chips */}
                    {designJob.spec && (
                      <div className="p-4 space-y-3 border-t border-neutral-800/50">
                        <div className="grid grid-cols-2 gap-2">
                          <div className="bg-neutral-900/60 border border-neutral-800/40 p-2.5 rounded-xl">
                            <div className="text-[10px] text-neutral-500 mb-1.5 flex items-center gap-1 uppercase tracking-wider">
                              <Palette size={10} /> Palette
                            </div>
                            <div className="flex gap-1.5 flex-wrap">
                              {designJob.spec.colors?.slice(0, 5).map(c => (
                                <div key={c} className="w-5 h-5 rounded-full border-2 border-neutral-700/60 shadow-sm" style={{ backgroundColor: c }} title={c} />
                              ))}
                            </div>
                          </div>
                          <div className="bg-neutral-900/60 border border-neutral-800/40 p-2.5 rounded-xl">
                            <div className="text-[10px] text-neutral-500 mb-1.5 flex items-center gap-1 uppercase tracking-wider">
                              <Leaf size={10} className="text-emerald-500" /> Eco Score
                            </div>
                            <div className="flex items-end gap-1">
                              <span className="text-lg font-bold text-emerald-400 leading-none">{designJob.spec.sustainability_score || 80}</span>
                              <span className="text-[10px] text-neutral-600 mb-0.5">/100</span>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={handleSaveDesign}
                            className={`py-2.5 rounded-xl text-xs font-semibold transition-all border
                              ${savePulse
                                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
                                : 'bg-neutral-800/60 border-neutral-700/40 text-neutral-300 hover:bg-neutral-800'}`}
                          >
                            {savePulse ? '✓ Saved!' : 'Save Design'}
                          </button>
                          <button
                            onClick={() => setActiveTab('tryon')}
                            className="py-2.5 rounded-xl text-xs font-semibold bg-white text-black hover:bg-neutral-100 transition-colors"
                          >
                            Try On →
                          </button>
                        </div>
                        <button
                          onClick={() => setShowTechPack(true)}
                          className="w-full border border-dashed border-neutral-700/50 text-neutral-500 hover:text-neutral-300 hover:border-neutral-600 py-2 rounded-xl text-xs font-medium transition-colors flex items-center justify-center gap-1.5"
                        >
                          <FileText size={11} /> Generate Tech Pack
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Smart Shopping */}
                  <div className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl overflow-hidden flex flex-col">
                    <div className="px-5 py-3.5 border-b border-neutral-800/50 flex items-center justify-between">
                      <span className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
                        <ShoppingBag size={13} className="text-violet-400" /> Buy Similar
                      </span>
                      <span className="text-[10px] text-neutral-600">AI-matched · 3 results</span>
                    </div>
                    <div className="p-4 space-y-3 overflow-y-auto">
                      {designJob.products.map((p, idx) => (
                        <div
                          key={idx}
                          className="bg-[#080808] border border-neutral-800/50 hover:border-neutral-700 rounded-xl p-4 transition-all hover:-translate-y-px group/card"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="text-sm font-medium text-neutral-200 leading-snug flex-1 pr-2">{p.name}</h4>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md shrink-0 ${
                              p.similarity_score >= 90 ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' :
                              'text-amber-400 bg-amber-500/10 border border-amber-500/20'}`}>
                              {p.similarity_score}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-[11px] text-neutral-600 block">{p.platform}</span>
                              <span className="text-neutral-100 font-bold text-base">₹{p.price.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="flex flex-col items-end gap-1">
                              <span className="text-[9px] text-violet-400 bg-violet-400/10 border border-violet-400/20 px-2 py-0.5 rounded-full">{p.tag}</span>
                              <button className="text-[11px] text-neutral-500 hover:text-white flex items-center gap-0.5 transition-colors">
                                View <ChevronRight size={10} />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                /* Empty / Processing state */
                <div className="bg-neutral-900/30 border border-neutral-800/40 rounded-2xl min-h-[480px] flex flex-col items-center justify-center text-center p-12">
                  {designJob.status === 'processing' ? (
                    <div className="space-y-4">
                      <div className="relative mx-auto w-12 h-12">
                        <div className="absolute inset-0 rounded-full border-2 border-neutral-800" />
                        <div className="absolute inset-0 rounded-full border-2 border-t-violet-500 animate-spin" />
                      </div>
                      <p className="text-sm text-neutral-500">Generating your design…</p>
                      <p className="text-xs text-neutral-700">This may take a few seconds</p>
                    </div>
                  ) : designJob.status === 'failed' ? (
                    <div className="space-y-3">
                      <div className="text-2xl">⚠️</div>
                      <p className="text-sm text-neutral-400">Generation failed. Please try again.</p>
                      <button onClick={() => handleGenerateDesign()} className="text-xs text-violet-400 hover:text-violet-300">Retry</button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="w-12 h-12 bg-neutral-800/60 rounded-2xl flex items-center justify-center mx-auto">
                        <Sparkles size={20} className="text-neutral-600" />
                      </div>
                      <p className="text-sm text-neutral-500">Describe your design and hit Generate</p>
                      <p className="text-xs text-neutral-700">Works in mock mode — no API key needed</p>
                    </div>
                  )}
                </div>
              )}
            </section>
          </div>
        )}

        {/* ════════════ TRY-ON ════════════ */}
        {activeTab === 'tryon' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-neutral-200">Virtual Try-On Room</h2>
                <p className="text-xs text-neutral-600 mt-0.5">Upload your photo · select a design · see the result</p>
              </div>
              {!designJob.image && (
                <button
                  onClick={() => setActiveTab('design')}
                  className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1 bg-violet-400/10 border border-violet-400/20 px-3 py-1.5 rounded-lg transition-colors"
                >
                  <Sparkles size={11} /> Generate a design first
                </button>
              )}
            </div>

            <div className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Step 1 */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 bg-neutral-800 border border-neutral-700 rounded-full flex items-center justify-center text-[10px] font-bold text-neutral-400">1</span>
                    <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Your Photo</h3>
                    {personImage && bodyAnalysis === null && <Loader2 size={11} className="animate-spin text-emerald-400 ml-auto" />}
                  </div>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="aspect-[3/4] bg-[#080808] border-2 border-dashed border-neutral-800 hover:border-neutral-600 rounded-xl flex items-center justify-center cursor-pointer overflow-hidden relative transition-colors group/upload"
                  >
                    {personImage ? (
                      <img src={personImage} className="w-full h-full object-cover" alt="Person" />
                    ) : (
                      <div className="text-center space-y-2">
                        <Upload size={18} className="text-neutral-700 mx-auto group-hover/upload:text-neutral-500 transition-colors" />
                        <p className="text-[11px] text-neutral-700 group-hover/upload:text-neutral-500 transition-colors">Click to upload</p>
                      </div>
                    )}
                    <input type="file" ref={fileInputRef} onChange={handlePersonUpload} className="hidden" accept="image/*" />
                  </div>
                  {bodyAnalysis && (
                    <div className="bg-emerald-500/5 border border-emerald-500/20 p-3 rounded-xl text-xs space-y-1">
                      <div className="text-emerald-400 font-semibold flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        Body Analysis Complete
                      </div>
                      <p className="text-neutral-400">Type: {bodyAnalysis.shape}</p>
                      <p className="text-neutral-600 text-[10px] leading-relaxed">{bodyAnalysis.tips}</p>
                    </div>
                  )}
                </div>

                {/* Step 2 */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 bg-neutral-800 border border-neutral-700 rounded-full flex items-center justify-center text-[10px] font-bold text-neutral-400">2</span>
                    <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Garment</h3>
                  </div>
                  <div className="aspect-[3/4] bg-[#080808] border border-neutral-800/60 rounded-xl flex items-center justify-center overflow-hidden">
                    {designJob.image
                      ? <img src={designJob.image} className="w-full h-full object-cover" alt="Garment" />
                      : <div className="text-center space-y-2">
                          <ImageIcon size={18} className="text-neutral-800 mx-auto" />
                          <p className="text-[11px] text-neutral-700">No design yet</p>
                        </div>}
                  </div>
                </div>

                {/* Step 3 */}
                <div className="space-y-3 flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 bg-neutral-800 border border-neutral-700 rounded-full flex items-center justify-center text-[10px] font-bold text-neutral-400">3</span>
                    <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Result</h3>
                  </div>
                  <div className="flex-1 bg-[#080808] border border-neutral-800/60 rounded-xl flex items-center justify-center overflow-hidden min-h-[200px] relative">
                    {tryOnJob.status === 'processing' ? (
                      <div className="text-center space-y-2">
                        <div className="relative w-8 h-8 mx-auto">
                          <div className="absolute inset-0 rounded-full border-2 border-neutral-800" />
                          <div className="absolute inset-0 rounded-full border-2 border-t-violet-500 animate-spin" />
                        </div>
                        <p className="text-[11px] text-neutral-600">Aligning garment…</p>
                      </div>
                    ) : tryOnJob.resultImage ? (
                      <>
                        <img src={tryOnJob.resultImage} className="w-full h-full object-cover" alt="Try-on result" />
                        <button
                          onClick={() => setExpandedImage(tryOnJob.resultImage)}
                          className="absolute bottom-2 right-2 bg-black/60 backdrop-blur p-1.5 rounded-lg text-white border border-white/10"
                        >
                          <Maximize2 size={12} />
                        </button>
                      </>
                    ) : (
                      <div className="text-center space-y-2">
                        <User size={18} className="text-neutral-800 mx-auto" />
                        <p className="text-[11px] text-neutral-700">Result appears here</p>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleTryOn}
                    disabled={!personImage || !designJob.image || tryOnJob.status === 'processing'}
                    className="w-full bg-white text-black py-2.5 rounded-xl text-sm font-semibold hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    {tryOnJob.status === 'processing' ? 'Processing…' : 'Virtual Try-On'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ COLLECTION ════════════ */}
        {activeTab === 'collection' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-neutral-200">Saved Designs</h2>
                <p className="text-xs text-neutral-600 mt-0.5">{savedDesigns.length} design{savedDesigns.length !== 1 ? 's' : ''} · price alerts enabled</p>
              </div>
              {savedDesigns.length > 0 && (
                <button
                  onClick={() => setActiveTab('design')}
                  className="text-xs text-neutral-500 hover:text-neutral-300 flex items-center gap-1 transition-colors"
                >
                  + New design
                </button>
              )}
            </div>

            {savedDesigns.length === 0 ? (
              <div className="bg-neutral-900/30 border border-neutral-800/40 rounded-2xl p-16 text-center">
                <div className="w-12 h-12 bg-neutral-800/60 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Layers size={20} className="text-neutral-600" />
                </div>
                <p className="text-sm text-neutral-500 mb-1">No designs saved yet</p>
                <p className="text-xs text-neutral-700 mb-4">Generate a design and hit "Save Design" to build your collection</p>
                <button
                  onClick={() => setActiveTab('design')}
                  className="inline-flex items-center gap-2 text-xs text-violet-400 bg-violet-400/10 border border-violet-400/20 px-4 py-2 rounded-lg hover:bg-violet-400/20 transition-colors"
                >
                  <Sparkles size={11} /> Go to Studio
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {savedDesigns.map(design => (
                  <div
                    key={design.id}
                    className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl overflow-hidden flex flex-col group hover:border-neutral-700/80 transition-all hover:-translate-y-0.5"
                  >
                    <div className="h-52 overflow-hidden bg-neutral-950 relative">
                      <img src={design.image} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt="Saved design" />
                      <button
                        onClick={() => setExpandedImage(design.image)}
                        className="absolute top-2 right-2 bg-black/50 backdrop-blur p-1.5 rounded-lg text-white/70 hover:text-white border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Maximize2 size={12} />
                      </button>
                    </div>
                    <div className="p-3.5 flex flex-col gap-2.5 flex-1">
                      <p className="text-[11px] text-neutral-400 line-clamp-2 leading-relaxed flex-1">{design.prompt}</p>
                      {design.spec && (
                        <div className="flex gap-1">
                          {design.spec.colors?.slice(0, 4).map(c => (
                            <div key={c} className="w-3 h-3 rounded-full border border-neutral-700/60" style={{ backgroundColor: c }} />
                          ))}
                          <span className="ml-auto text-[10px] text-emerald-500">{design.spec.sustainability_score || 80}/100 eco</span>
                        </div>
                      )}
                      <div className="flex items-center justify-between pt-2 border-t border-neutral-800/40">
                        <button
                          onClick={() => setSavedDesigns(StorageService.toggleTrack(design.id))}
                          className={`flex items-center gap-1 text-[10px] font-medium transition-colors ${design.isTracking ? 'text-emerald-400' : 'text-neutral-600 hover:text-neutral-400'}`}
                        >
                          {design.isTracking ? <BellRing size={11} /> : <Bell size={11} />}
                          {design.isTracking ? 'Tracking' : 'Track'}
                        </button>
                        <div className="flex gap-2.5 items-center">
                          <button
                            onClick={() => handleGenerateDesign(design.prompt)}
                            className="text-neutral-600 hover:text-violet-400 transition-colors"
                            title="Remix"
                          >
                            <RefreshCw size={12} />
                          </button>
                          <button
                            onClick={() => { StorageService.deleteDesign(design.id); setSavedDesigns(StorageService.getCollections()); }}
                            className="text-neutral-700 hover:text-red-400 transition-colors"
                            title="Delete"
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
    </div>
  );
}
