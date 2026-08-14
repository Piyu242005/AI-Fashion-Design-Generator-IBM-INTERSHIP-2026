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
  Bell, BellRing, Activity, Wand2,
  ArrowRight, Cpu, Plus, Copy, Check, Columns2
} from 'lucide-react';

/* ─── CONFIG ──────────────────────────────────────────────────────── */
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "";
const GEMINI_MODEL   = import.meta.env.VITE_GEMINI_MODEL   || "gemini-2.5-flash";

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
      const res = await fetch('/api/design', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (res.ok) { const data = await res.json(); if (data.success && data.image) return data.image; }
      else { const err = await res.json().catch(() => ({})); if (res.status !== 503) console.warn('[ImageGen] CF error:', err?.error?.code); }
    } catch (e) { console.warn('[ImageGen] /api/design unreachable:', e.message); }
    return null;
  }
};

/* ─── PRODUCT SEARCH SERVICE ──────────────────────────────────── */
// Calls the Vercel /api/products/search serverless function.
// The RapidAPI key lives ONLY in server-side env vars — never in the browser bundle.
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

      const res = await fetch(`/api/products/search?${params}`);

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

/* ─── 100 GARMENT SAMPLES (Unsplash open-source) ─────────────────── */
const GARMENT_SAMPLES = [
  { id:"gs1",  label:"White Linen Shirt",          category:"Shirts",   url:"https://images.unsplash.com/photo-1598032895397-b9472444bf93?w=400&q=80" },
  { id:"gs2",  label:"Black V-Neck Tee",           category:"Shirts",   url:"https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&q=80" },
  { id:"gs3",  label:"Striped Oxford Shirt",       category:"Shirts",   url:"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&q=80" },
  { id:"gs4",  label:"Pastel Pink Blouse",         category:"Shirts",   url:"https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=400&q=80" },
  { id:"gs5",  label:"Navy Polo Shirt",            category:"Shirts",   url:"https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400&q=80" },
  { id:"gs6",  label:"Graphic Tee – Abstract",     category:"Shirts",   url:"https://images.unsplash.com/photo-1529374255404-311a2a4f1fd9?w=400&q=80" },
  { id:"gs7",  label:"Chambray Button-Down",       category:"Shirts",   url:"https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&q=80" },
  { id:"gs8",  label:"Cropped Tank Top",           category:"Shirts",   url:"https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=400&q=80" },
  { id:"gs9",  label:"Off-Shoulder Top",           category:"Shirts",   url:"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80" },
  { id:"gs10", label:"Ruffle Sleeve Blouse",       category:"Shirts",   url:"https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400&q=80" },
  { id:"gs11", label:"High-Waist Skinny Jeans",    category:"Bottoms",  url:"https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80" },
  { id:"gs12", label:"Wide-Leg Trousers",          category:"Bottoms",  url:"https://images.unsplash.com/photo-1604176354204-9268737828e4?w=400&q=80" },
  { id:"gs13", label:"Pleated Mini Skirt",         category:"Bottoms",  url:"https://images.unsplash.com/photo-1577900232427-18219b9166a0?w=400&q=80" },
  { id:"gs14", label:"Denim Shorts",               category:"Bottoms",  url:"https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=400&q=80" },
  { id:"gs15", label:"Floral Wrap Skirt",          category:"Bottoms",  url:"https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80" },
  { id:"gs16", label:"Black Leggings",             category:"Bottoms",  url:"https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&q=80" },
  { id:"gs17", label:"Cargo Pants",                category:"Bottoms",  url:"https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=400&q=80" },
  { id:"gs18", label:"Linen Wide Pants",           category:"Bottoms",  url:"https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=400&q=80" },
  { id:"gs19", label:"Corduroy Trousers",          category:"Bottoms",  url:"https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400&q=80" },
  { id:"gs20", label:"Bermuda Shorts",             category:"Bottoms",  url:"https://images.unsplash.com/photo-1565084888279-aca607bb7621?w=400&q=80" },
  { id:"gs21", label:"Floral Maxi Dress",          category:"Dresses",  url:"https://images.unsplash.com/photo-1496217590455-aa63a8350eea?w=400&q=80" },
  { id:"gs22", label:"Little Black Dress",         category:"Dresses",  url:"https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80" },
  { id:"gs23", label:"Wrap Midi Dress",            category:"Dresses",  url:"https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=400&q=80" },
  { id:"gs24", label:"Slip Satin Dress",           category:"Dresses",  url:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80" },
  { id:"gs25", label:"Sundress – Yellow Print",    category:"Dresses",  url:"https://images.unsplash.com/photo-1603344204980-4edb0ea63148?w=400&q=80" },
  { id:"gs26", label:"Shirt Dress",                category:"Dresses",  url:"https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=400&q=80" },
  { id:"gs27", label:"Bodycon Dress",              category:"Dresses",  url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=400&q=80" },
  { id:"gs28", label:"Tiered Boho Dress",          category:"Dresses",  url:"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80" },
  { id:"gs29", label:"Flared Denim Dress",         category:"Dresses",  url:"https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=400&q=80" },
  { id:"gs30", label:"Summer Co-ord Set",          category:"Dresses",  url:"https://images.unsplash.com/photo-1589810635657-232948472d98?w=400&q=80" },
  { id:"gs31", label:"Classic Navy Blazer",        category:"Formal",   url:"https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&q=80" },
  { id:"gs32", label:"Pinstripe Suit Jacket",      category:"Formal",   url:"https://images.unsplash.com/photo-1593032465175-481ac7f401a0?w=400&q=80" },
  { id:"gs33", label:"Double-Breasted Blazer",     category:"Formal",   url:"https://images.unsplash.com/photo-1617952739355-46d61416648e?w=400&q=80" },
  { id:"gs34", label:"White Tailored Shirt",       category:"Formal",   url:"https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400&q=80" },
  { id:"gs35", label:"Black Formal Trousers",      category:"Formal",   url:"https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80" },
  { id:"gs36", label:"Tuxedo Jacket",              category:"Formal",   url:"https://images.unsplash.com/photo-1564564321837-a57b7070ac4f?w=400&q=80" },
  { id:"gs37", label:"Pencil Skirt – Black",       category:"Formal",   url:"https://images.unsplash.com/photo-1594938298603-c8148c4b4086?w=400&q=80" },
  { id:"gs38", label:"Structured Blazer Dress",    category:"Formal",   url:"https://images.unsplash.com/photo-1614676471928-2ed0ad1061a4?w=400&q=80" },
  { id:"gs39", label:"Grey Suit Trousers",         category:"Formal",   url:"https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80" },
  { id:"gs40", label:"Crepe Formal Blouse",        category:"Formal",   url:"https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&q=80" },
  { id:"gs41", label:"Olive Cargo Jacket",         category:"Jackets",  url:"https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80" },
  { id:"gs42", label:"Classic Denim Jacket",       category:"Jackets",  url:"https://images.unsplash.com/photo-1542295669297-4d352b042bca?w=400&q=80" },
  { id:"gs43", label:"Beige Trench Coat",          category:"Jackets",  url:"https://images.unsplash.com/photo-1548454782-15b189d129ab?w=400&q=80" },
  { id:"gs44", label:"Puffer Jacket – Black",      category:"Jackets",  url:"https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400&q=80" },
  { id:"gs45", label:"Brown Leather Jacket",       category:"Jackets",  url:"https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=400&q=80" },
  { id:"gs46", label:"Oversized Bomber",           category:"Jackets",  url:"https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&q=80" },
  { id:"gs47", label:"Checked Shacket",            category:"Jackets",  url:"https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400&q=80" },
  { id:"gs48", label:"Windbreaker",                category:"Jackets",  url:"https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80" },
  { id:"gs49", label:"Faux-Fur Coat",              category:"Jackets",  url:"https://images.unsplash.com/photo-1520975867351-d91ff4fa57d9?w=400&q=80" },
  { id:"gs50", label:"Cropped Blazer – Cream",     category:"Jackets",  url:"https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80" },
  { id:"gs51", label:"Grey Marl Hoodie",           category:"Casual",   url:"https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&q=80" },
  { id:"gs52", label:"White Oversized Tee",        category:"Casual",   url:"https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80" },
  { id:"gs53", label:"Blue Sweatshirt",            category:"Casual",   url:"https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=400&q=80" },
  { id:"gs54", label:"Vintage Denim Jacket",       category:"Casual",   url:"https://images.unsplash.com/photo-1588099768523-f4e6a5679d88?w=400&q=80" },
  { id:"gs55", label:"Knit Cardigan – Beige",      category:"Casual",   url:"https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80" },
  { id:"gs56", label:"Track Jacket",               category:"Casual",   url:"https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80" },
  { id:"gs57", label:"Zip-Up Fleece",              category:"Casual",   url:"https://images.unsplash.com/photo-1603344204980-4edb0ea63148?w=400&q=80" },
  { id:"gs58", label:"Crewneck Sweatshirt",        category:"Casual",   url:"https://images.unsplash.com/photo-1578632767115-351597cf2477?w=400&q=80" },
  { id:"gs59", label:"Tie-Dye Tee",               category:"Casual",   url:"https://images.unsplash.com/photo-1529374255404-311a2a4f1fd9?w=400&q=80" },
  { id:"gs60", label:"Striped Breton Top",         category:"Casual",   url:"https://images.unsplash.com/photo-1618354691438-25bc04584c23?w=400&q=80" },
  { id:"gs61", label:"Pastel Kurta",               category:"Ethnic",   url:"https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=400&q=80" },
  { id:"gs62", label:"Embroidered Anarkali",       category:"Ethnic",   url:"https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=400&q=80" },
  { id:"gs63", label:"Silk Saree – Teal",          category:"Ethnic",   url:"https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&q=80" },
  { id:"gs64", label:"Bandhani Dress",             category:"Ethnic",   url:"https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=400&q=80" },
  { id:"gs65", label:"Block-Print Co-ord",         category:"Ethnic",   url:"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&q=80" },
  { id:"gs66", label:"Indo-Western Jacket",        category:"Ethnic",   url:"https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=400&q=80" },
  { id:"gs67", label:"Chikankari Kurti",           category:"Ethnic",   url:"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80" },
  { id:"gs68", label:"Lehenga – Blush Pink",       category:"Ethnic",   url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=400&q=80" },
  { id:"gs69", label:"Dhoti Pants Set",            category:"Ethnic",   url:"https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=400&q=80" },
  { id:"gs70", label:"Phulkari Jacket",            category:"Ethnic",   url:"https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400&q=80" },
  { id:"gs71", label:"Zip-Up Hoodie – Black",      category:"Activewear", url:"https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=400&q=80" },
  { id:"gs72", label:"Sports Bra – Coral",         category:"Activewear", url:"https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=400&q=80" },
  { id:"gs73", label:"Yoga Leggings",              category:"Activewear", url:"https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&q=80" },
  { id:"gs74", label:"Running Jacket",             category:"Activewear", url:"https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80" },
  { id:"gs75", label:"Athletic Shorts",            category:"Activewear", url:"https://images.unsplash.com/photo-1565084888279-aca607bb7621?w=400&q=80" },
  { id:"gs76", label:"Tank Top – Racerback",       category:"Activewear", url:"https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=400&q=80" },
  { id:"gs77", label:"Compression Tee",            category:"Activewear", url:"https://images.unsplash.com/photo-1578632767115-351597cf2477?w=400&q=80" },
  { id:"gs78", label:"Cycling Shorts",             category:"Activewear", url:"https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80" },
  { id:"gs79", label:"Windproof Gilet",            category:"Activewear", url:"https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400&q=80" },
  { id:"gs80", label:"Gym Sweatpants",             category:"Activewear", url:"https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80" },
  { id:"gs81", label:"Cashmere V-Neck Sweater",    category:"Knitwear",  url:"https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&q=80" },
  { id:"gs82", label:"Chunky Knit Turtleneck",     category:"Knitwear",  url:"https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80" },
  { id:"gs83", label:"Cable Knit Cardigan",        category:"Knitwear",  url:"https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&q=80" },
  { id:"gs84", label:"Merino Wool Jumper",         category:"Knitwear",  url:"https://images.unsplash.com/photo-1520975867351-d91ff4fa57d9?w=400&q=80" },
  { id:"gs85", label:"Ribbed Crop Sweater",        category:"Knitwear",  url:"https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=400&q=80" },
  { id:"gs86", label:"Striped Knit Vest",          category:"Knitwear",  url:"https://images.unsplash.com/photo-1618354691438-25bc04584c23?w=400&q=80" },
  { id:"gs87", label:"Longline Cardigan",          category:"Knitwear",  url:"https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80" },
  { id:"gs88", label:"Open-Front Kimono",          category:"Knitwear",  url:"https://images.unsplash.com/photo-1589810635657-232948472d98?w=400&q=80" },
  { id:"gs89", label:"Oversized Roll-Neck",        category:"Knitwear",  url:"https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&q=80" },
  { id:"gs90", label:"Fair-Isle Sweater",          category:"Knitwear",  url:"https://images.unsplash.com/photo-1614676471928-2ed0ad1061a4?w=400&q=80" },
  { id:"gs91", label:"Evening Gown – Navy",        category:"Evening",   url:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80" },
  { id:"gs92", label:"Sequin Mini Dress",          category:"Evening",   url:"https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=400&q=80" },
  { id:"gs93", label:"Velvet Blazer",              category:"Evening",   url:"https://images.unsplash.com/photo-1617952739355-46d61416648e?w=400&q=80" },
  { id:"gs94", label:"Backless Maxi Dress",        category:"Evening",   url:"https://images.unsplash.com/photo-1496217590455-aa63a8350eea?w=400&q=80" },
  { id:"gs95", label:"Slit Satin Gown",            category:"Evening",   url:"https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400&q=80" },
  { id:"gs96", label:"Feather-Trim Blouse",        category:"Evening",   url:"https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=400&q=80" },
  { id:"gs97", label:"Cocktail Wrap Dress",        category:"Evening",   url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=400&q=80" },
  { id:"gs98", label:"Lace Midi Dress",            category:"Evening",   url:"https://images.unsplash.com/photo-1603344204980-4edb0ea63148?w=400&q=80" },
  { id:"gs99", label:"Tuxedo Jumpsuit",            category:"Evening",   url:"https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80" },
  { id:"gs100",label:"Gold Brocade Kurta Set",     category:"Evening",   url:"https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&q=80" },
];

/* ─── 50 FEMALE MODELS (Unsplash open-source) ────────────────────── */
/* ─── MODEL PHOTO DATA (kept for Model Photos sub-tab) ───────────── */
const FEMALE_MODELS = [
  { id:"fm1",  label:"Elegant Formal Look",   url:"https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400&q=80" },
  { id:"fm2",  label:"Street Style Casual",   url:"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80" },
  { id:"fm3",  label:"Summer Floral Dress",   url:"https://images.unsplash.com/photo-1496217590455-aa63a8350eea?w=400&q=80" },
  { id:"fm4",  label:"Minimal White Outfit",  url:"https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80" },
  { id:"fm5",  label:"Boho Chic Look",        url:"https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&q=80" },
  { id:"fm6",  label:"Editorial Black Dress", url:"https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80" },
  { id:"fm7",  label:"Corporate Blazer",      url:"https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80" },
  { id:"fm8",  label:"Resort Wear Look",      url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=400&q=80" },
  { id:"fm9",  label:"Monochrome Grey Set",   url:"https://images.unsplash.com/photo-1546961342-ea5f62d5a27b?w=400&q=80" },
  { id:"fm10", label:"Red Evening Gown",      url:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80" },
  { id:"fm11", label:"Denim-on-Denim",        url:"https://images.unsplash.com/photo-1588099768523-f4e6a5679d88?w=400&q=80" },
  { id:"fm12", label:"Pastel Co-ord",         url:"https://images.unsplash.com/photo-1589810635657-232948472d98?w=400&q=80" },
  { id:"fm13", label:"High Fashion Couture",  url:"https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400&q=80" },
  { id:"fm14", label:"Sporty Casual Mix",     url:"https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&q=80" },
  { id:"fm15", label:"Wrap Dress Look",       url:"https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=400&q=80" },
  { id:"fm16", label:"Knit Sweater & Jeans",  url:"https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&q=80" },
  { id:"fm17", label:"Smart Casual Blazer",   url:"https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&q=80" },
  { id:"fm18", label:"Vintage-Inspired Look", url:"https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=400&q=80" },
  { id:"fm19", label:"Ethnic Fusion Style",   url:"https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=400&q=80" },
  { id:"fm20", label:"Summer Beach Attire",   url:"https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&q=80" },
  { id:"fm21", label:"Classic Trench",        url:"https://images.unsplash.com/photo-1548454782-15b189d129ab?w=400&q=80" },
  { id:"fm22", label:"Monochrome Black",      url:"https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=400&q=80" },
  { id:"fm23", label:"Soft Neutral Palette",  url:"https://images.unsplash.com/photo-1614676471928-2ed0ad1061a4?w=400&q=80" },
  { id:"fm24", label:"Bold Color Block",      url:"https://images.unsplash.com/photo-1617952739355-46d61416648e?w=400&q=80" },
  { id:"fm25", label:"Night-Out Look",        url:"https://images.unsplash.com/photo-1609803384069-19f3f6e2d5c1?w=400&q=80" },
  { id:"fm26", label:"Off-Shoulder Maxi",     url:"https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=400&q=80" },
  { id:"fm27", label:"Leather Jacket Edge",   url:"https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=400&q=80" },
  { id:"fm28", label:"Spring Garden Look",    url:"https://images.unsplash.com/photo-1603344204980-4edb0ea63148?w=400&q=80" },
  { id:"fm29", label:"Linen Relaxed Outfit",  url:"https://images.unsplash.com/photo-1590736969596-77e04f0c2a0a?w=400&q=80" },
  { id:"fm30", label:"Structured Suit Set",   url:"https://images.unsplash.com/photo-1614201061439-c86c1de7c37a?w=400&q=80" },
  { id:"fm31", label:"Ruched Mini Dress",     url:"https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80" },
  { id:"fm32", label:"Cozy Oversized Knit",   url:"https://images.unsplash.com/photo-1578632767115-351597cf2477?w=400&q=80" },
  { id:"fm33", label:"Midi Skirt & Crop",     url:"https://images.unsplash.com/photo-1577900232427-18219b9166a0?w=400&q=80" },
  { id:"fm34", label:"Asymmetric Hem Dress",  url:"https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=400&q=80" },
  { id:"fm35", label:"Collarless Blazer",     url:"https://images.unsplash.com/photo-1604176354204-9268737828e4?w=400&q=80" },
  { id:"fm36", label:"Printed Wrap Top",      url:"https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=400&q=80" },
  { id:"fm37", label:"Classic White Set",     url:"https://images.unsplash.com/photo-1598032895397-b9472444bf93?w=400&q=80" },
  { id:"fm38", label:"High-Neck Bodysuit",    url:"https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&q=80" },
  { id:"fm39", label:"Flowy Palazzo Pants",   url:"https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80" },
  { id:"fm40", label:"Sequined Party Dress",  url:"https://images.unsplash.com/photo-1593032465175-481ac7f401a0?w=400&q=80" },
  { id:"fm41", label:"Peplum & Slacks",       url:"https://images.unsplash.com/photo-1594938298603-c8148c4b4086?w=400&q=80" },
  { id:"fm42", label:"Tank & Joggers",        url:"https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=400&q=80" },
  { id:"fm43", label:"Checked Blazer",        url:"https://images.unsplash.com/photo-1547496502-affa22d38842?w=400&q=80" },
  { id:"fm44", label:"Velvet Evening Look",   url:"https://images.unsplash.com/photo-1470506926202-05d3fca84c9a?w=400&q=80" },
  { id:"fm45", label:"Crop Top & Maxi",       url:"https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&q=80" },
  { id:"fm46", label:"Breezy Linen Set",      url:"https://images.unsplash.com/photo-1520975867351-d91ff4fa57d9?w=400&q=80" },
  { id:"fm47", label:"Sporty Chic",           url:"https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=400&q=80" },
  { id:"fm48", label:"Satin Slip Ensemble",   url:"https://images.unsplash.com/photo-1536766768598-e09213fdcf22?w=400&q=80" },
  { id:"fm49", label:"Flare Jeans & Blouse",  url:"https://images.unsplash.com/photo-1541727130-6df27d17ab59?w=400&q=80" },
  { id:"fm50", label:"Bold Print Co-ord",     url:"https://images.unsplash.com/photo-1589810635657-232948472d98?w=400&q=80" },
];

const MALE_MODELS = [
  { id:"mm1",  label:"Casual White Tee",      url:"https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80" },
  { id:"mm2",  label:"Smart Casual Blazer",   url:"https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&q=80" },
  { id:"mm3",  label:"Streetwear Hoodie",     url:"https://images.unsplash.com/photo-1568602471122-7832951cc4c5?w=400&q=80" },
  { id:"mm4",  label:"Business Formal Suit",  url:"https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80" },
  { id:"mm5",  label:"Denim & Graphic Tee",   url:"https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=400&q=80" },
  { id:"mm6",  label:"Athletic Sportswear",   url:"https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80" },
  { id:"mm7",  label:"Linen Shirt Beach",     url:"https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80" },
  { id:"mm8",  label:"Black Turtleneck",      url:"https://images.unsplash.com/photo-1564564321837-a57b7070ac4f?w=400&q=80" },
  { id:"mm9",  label:"Leather Jacket Look",   url:"https://images.unsplash.com/photo-1541577141970-eebc83ebe30e?w=400&q=80" },
  { id:"mm10", label:"Polo & Chinos",         url:"https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80" },
  { id:"mm11", label:"Trench Coat Winter",    url:"https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&q=80" },
  { id:"mm12", label:"Summer Shorts & Shirt", url:"https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400&q=80" },
  { id:"mm13", label:"Bold Pattern Shirt",    url:"https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=80" },
  { id:"mm14", label:"Knit Sweater Smart",    url:"https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?w=400&q=80" },
  { id:"mm15", label:"Monochrome Black",      url:"https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&q=80" },
  { id:"mm16", label:"Traditional Ethnic",    url:"https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=400&q=80" },
  { id:"mm17", label:"Bomber Jacket Street",  url:"https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&q=80" },
  { id:"mm18", label:"Fitted Crew Neck Tee",  url:"https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&q=80" },
  { id:"mm19", label:"Formal White Shirt",    url:"https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400&q=80" },
  { id:"mm20", label:"Casual Weekend",        url:"https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&q=80" },
];

/* ─── FASHION MODELS DIRECTORY — 50 fictional editorial models ──────
   All photos: Unsplash free-to-use portraits (professional, tasteful,
   no nudity). Fictional names + bios for fashion-editorial context.
─────────────────────────────────────────────────────────────────── */
const FASHION_MODELS = [
  // ── USA ──────────────────────────────────────────────────────────
  { id:"p1",  name:"Savannah Brooks",    country:"USA",        region:"Americas",
    specialty:"High Fashion / Runway",
    bio:"NYC-based editorial model known for her striking minimalist looks and New York Fashion Week appearances.",
    url:"https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&q=85" },
  { id:"p2",  name:"Maya Delacroix",     country:"USA",        region:"Americas",
    specialty:"Commercial / Lifestyle",
    bio:"Versatile Los Angeles model who has fronted campaigns for major denim and streetwear brands.",
    url:"https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=500&q=85" },
  { id:"p3",  name:"Jordan Vale",        country:"USA",        region:"Americas",
    specialty:"Fitness & Activewear",
    bio:"Sports-editorial specialist based in Miami; collaborates with athleisure labels across the US.",
    url:"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&q=85" },
  { id:"p4",  name:"Camille Okafor",     country:"USA",        region:"Americas",
    specialty:"Couture / Evening Wear",
    bio:"Represented by a top Chicago agency, Camille is celebrated for her commanding presence on the couture circuit.",
    url:"https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=500&q=85" },
  { id:"p5",  name:"Tara Winslow",       country:"USA",        region:"Americas",
    specialty:"Print & Editorial",
    bio:"Vogue and Harper's Bazaar contributor whose work spans contemporary American fashion narratives.",
    url:"https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=500&q=85" },
  // ── India ─────────────────────────────────────────────────────────
  { id:"p6",  name:"Aaradhya Sharma",    country:"India",      region:"Asia",
    specialty:"Ethnic & Fusion Wear",
    bio:"Jaipur-born model who bridges traditional Indian textiles and contemporary international runways.",
    url:"https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=500&q=85" },
  { id:"p7",  name:"Priya Nair",         country:"India",      region:"Asia",
    specialty:"Bridal & Occasion Wear",
    bio:"Mumbai-based bridal specialist; known for her work with India's top couture houses and jewellery labels.",
    url:"https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=500&q=85" },
  { id:"p8",  name:"Divya Kapoor",       country:"India",      region:"Asia",
    specialty:"Commercial / Beauty",
    bio:"Delhi's most-booked beauty model with campaigns spanning skincare, fashion-tech, and luxury accessories.",
    url:"https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=85" },
  { id:"p9",  name:"Meera Joshi",        country:"India",      region:"Asia",
    specialty:"Street Style / Casual",
    bio:"Bangalore creative-scene regular who champions sustainable Indian labels on social and editorial platforms.",
    url:"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&q=85" },
  // ── Japan ─────────────────────────────────────────────────────────
  { id:"p10", name:"Haruka Mizuno",      country:"Japan",      region:"Asia",
    specialty:"Avant-Garde / Editorial",
    bio:"Tokyo fashion-week fixture renowned for her precise editorial expressions and harajuku-influenced styling.",
    url:"https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=500&q=85" },
  { id:"p11", name:"Yuki Tanaka",        country:"Japan",      region:"Asia",
    specialty:"Minimalist / Contemporary",
    bio:"Osaka-based model who specialises in clean, architectural silhouettes for luxury Japanese labels.",
    url:"https://images.unsplash.com/photo-1541727130-6df27d17ab59?w=500&q=85" },
  { id:"p12", name:"Aiko Hayashi",       country:"Japan",      region:"Asia",
    specialty:"Beauty / Cosmetics",
    bio:"The face of several international beauty campaigns, Aiko is celebrated for her versatile editorial range.",
    url:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&q=85" },
  // ── South Korea ───────────────────────────────────────────────────
  { id:"p13", name:"Ji-Yeon Park",       country:"South Korea",region:"Asia",
    specialty:"K-Fashion / Contemporary",
    bio:"Seoul street-fashion icon whose daily looks have earned her a dedicated global following.",
    url:"https://images.unsplash.com/photo-1609803384069-19f3f6e2d5c1?w=500&q=85" },
  { id:"p14", name:"Soo-Yeon Han",       country:"South Korea",region:"Asia",
    specialty:"Runway / Commercial",
    bio:"Seoul Fashion Week veteran who has walked for both emerging designers and established Korean houses.",
    url:"https://images.unsplash.com/photo-1546961342-ea5f62d5a27b?w=500&q=85" },
  // ── China ─────────────────────────────────────────────────────────
  { id:"p15", name:"Ling Wei Chen",      country:"China",      region:"Asia",
    specialty:"Luxury / Haute Couture",
    bio:"Shanghai-based luxury model who regularly appears in Vogue China and international high-fashion editorials.",
    url:"https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=500&q=85" },
  { id:"p16", name:"Xiu Mei Lu",         country:"China",      region:"Asia",
    specialty:"Sportswear & Active",
    bio:"Beijing model and fitness advocate, the face of several international athletic and wellness campaigns.",
    url:"https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&q=85" },
  // ── UK ────────────────────────────────────────────────────────────
  { id:"p17", name:"Eloise Pemberton",   country:"UK",         region:"Europe",
    specialty:"High Street & Editorial",
    bio:"London-born model whose effortless British style has graced covers from Elle to The Sunday Times Style.",
    url:"https://images.unsplash.com/photo-1617952739355-46d61416648e?w=500&q=85" },
  { id:"p18", name:"Imogen Clarke",      country:"UK",         region:"Europe",
    specialty:"Evening & Couture",
    bio:"Manchester native signed to a top London agency; known for her elegance on red carpets and editorial sets.",
    url:"https://images.unsplash.com/photo-1614676471928-2ed0ad1061a4?w=500&q=85" },
  // ── France ────────────────────────────────────────────────────────
  { id:"p19", name:"Céline Moreau",      country:"France",     region:"Europe",
    specialty:"Parisian Chic / Couture",
    bio:"Born in Lyon, Céline embodies effortless Parisian elegance with an edge — a fixture at Paris Fashion Week.",
    url:"https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=500&q=85" },
  { id:"p20", name:"Amélie Fontaine",    country:"France",     region:"Europe",
    specialty:"Fragrance & Beauty",
    bio:"The face of multiple international fragrance houses, Amélie's photogenic versatility spans print to film.",
    url:"https://images.unsplash.com/photo-1604176354204-9268737828e4?w=500&q=85" },
  // ── Italy ─────────────────────────────────────────────────────────
  { id:"p21", name:"Valentina Conti",    country:"Italy",      region:"Europe",
    specialty:"Luxury / Accessories",
    bio:"Milan-based luxury model whose campaigns for Italian leather houses define modern Italian sophistication.",
    url:"https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=500&q=85" },
  { id:"p22", name:"Gioia Ferraro",      country:"Italy",      region:"Europe",
    specialty:"Runway / Resort",
    bio:"Florence editorial model who splits her year between Milan shows and exclusive resort-wear shoots.",
    url:"https://images.unsplash.com/photo-1593032465175-481ac7f401a0?w=500&q=85" },
  // ── Germany ───────────────────────────────────────────────────────
  { id:"p23", name:"Lena Brandt",        country:"Germany",    region:"Europe",
    specialty:"Sportswear & Lifestyle",
    bio:"Hamburg model and brand ambassador for leading European activewear and outdoor lifestyle brands.",
    url:"https://images.unsplash.com/photo-1590736969596-77e04f0c2a0a?w=500&q=85" },
  // ── Spain ─────────────────────────────────────────────────────────
  { id:"p24", name:"Sofía Montoya",      country:"Spain",      region:"Europe",
    specialty:"Mediterranean Style",
    bio:"Barcelona-born with an infectious energy, Sofía works the boundary between street editorial and couture.",
    url:"https://images.unsplash.com/photo-1589810635657-232948472d98?w=500&q=85" },
  // ── Sweden ────────────────────────────────────────────────────────
  { id:"p25", name:"Astrid Lindqvist",   country:"Sweden",     region:"Europe",
    specialty:"Scandi Minimalism",
    bio:"Stockholm native whose clean, nordic aesthetic has made her a favourite for Scandinavian design labels.",
    url:"https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=500&q=85" },
  // ── Czech Republic ────────────────────────────────────────────────
  { id:"p26", name:"Karolína Horáčková", country:"Czech Republic", region:"Europe",
    specialty:"Editorial / High Fashion",
    bio:"Prague's leading editorial face; her striking bone structure has opened doors at top European agencies.",
    url:"https://images.unsplash.com/photo-1594938298603-c8148c4b4086?w=500&q=85" },
  // ── Poland ────────────────────────────────────────────────────────
  { id:"p27", name:"Zofia Wiśniewska",   country:"Poland",     region:"Europe",
    specialty:"Runway / Commercial",
    bio:"Warsaw-born model who has built a strong runway career across Warsaw, Berlin, and Paris fashion weeks.",
    url:"https://images.unsplash.com/photo-1614201061439-c86c1de7c37a?w=500&q=85" },
  // ── Russia / Eastern Europe ───────────────────────────────────────
  { id:"p28", name:"Natasha Volkov",     country:"Russia",     region:"Europe",
    specialty:"Editorial / Couture",
    bio:"Moscow-born model whose high-fashion editorial work has appeared in international editions of Vogue.",
    url:"https://images.unsplash.com/photo-1603344204980-4edb0ea63148?w=500&q=85" },
  // ── Ukraine ───────────────────────────────────────────────────────
  { id:"p29", name:"Oksana Petrenko",    country:"Ukraine",    region:"Europe",
    specialty:"Bridal & Occasion Wear",
    bio:"Kyiv-based bridal specialist who has redefined modern Eastern European bridal editorial photography.",
    url:"https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=500&q=85" },
  // ── Hungary ───────────────────────────────────────────────────────
  { id:"p30", name:"Éva Molnár",         country:"Hungary",    region:"Europe",
    specialty:"Runway / Campaign",
    bio:"Budapest native who turned heads at her first Budapest Fashion Week and has since gone international.",
    url:"https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500&q=85" },
  // ── Romania ───────────────────────────────────────────────────────
  { id:"p31", name:"Elena Ionescu",      country:"Romania",    region:"Europe",
    specialty:"Commercial / Beauty",
    bio:"Bucharest beauty model whose expressive editorial range has earned her placements across European campaigns.",
    url:"https://images.unsplash.com/photo-1577900232427-18219b9166a0?w=500&q=85" },
  // ── Brazil ────────────────────────────────────────────────────────
  { id:"p32", name:"Isabella Carvalho",  country:"Brazil",     region:"Americas",
    specialty:"Swimwear & Resort",
    bio:"São Paulo model and fitness influencer; the quintessential face of South American summer campaigns.",
    url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=500&q=85" },
  { id:"p33", name:"Bianca Ferreira",    country:"Brazil",     region:"Americas",
    specialty:"Street Style / Urban",
    bio:"Rio de Janeiro street-fashion powerhouse whose vibrant style captures the energy of Brazilian youth culture.",
    url:"https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=85" },
  // ── Colombia ──────────────────────────────────────────────────────
  { id:"p34", name:"Valeria Gómez",      country:"Colombia",   region:"Americas",
    specialty:"Runway / Commercial",
    bio:"Bogotá-born Valeria brings Latin warmth to the runway — a sought-after face for tropical and resort labels.",
    url:"https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=500&q=85" },
  // ── Canada ────────────────────────────────────────────────────────
  { id:"p35", name:"Natalie Rousseau",   country:"Canada",     region:"Americas",
    specialty:"Lifestyle & Commercial",
    bio:"Toronto-based model whose approachable aesthetic has made her a top choice for Canadian and US lifestyle brands.",
    url:"https://images.unsplash.com/photo-1520975867351-d91ff4fa57d9?w=500&q=85" },
  // ── Australia ─────────────────────────────────────────────────────
  { id:"p36", name:"Zara Mitchell",      country:"Australia",  region:"Oceania",
    specialty:"Outdoor & Beach Lifestyle",
    bio:"Sydney surf-and-style model who effortlessly transitions between beach campaigns and high-end editorial.",
    url:"https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=500&q=85" },
  // ── South Africa ──────────────────────────────────────────────────
  { id:"p37", name:"Amahle Dlamini",     country:"South Africa",region:"Africa",
    specialty:"Afro-Contemporary / Couture",
    bio:"Cape Town model who champions African design on international stages, appearing at Lagos and Paris shows.",
    url:"https://images.unsplash.com/photo-1536766768598-e09213fdcf22?w=500&q=85" },
  // ── Nigeria ───────────────────────────────────────────────────────
  { id:"p38", name:"Adaeze Okafor",      country:"Nigeria",    region:"Africa",
    specialty:"Editorial & African Fashion Week",
    bio:"Lagos model and advocate for African sustainable fashion; regular feature at Lagos Fashion Week.",
    url:"https://images.unsplash.com/photo-1470506926202-05d3fca84c9a?w=500&q=85" },
  // ── Ethiopia ──────────────────────────────────────────────────────
  { id:"p39", name:"Selam Bekele",       country:"Ethiopia",   region:"Africa",
    specialty:"Runway / International Editorial",
    bio:"Addis Ababa-born model whose regal presence has graced international campaigns from Paris to New York.",
    url:"https://images.unsplash.com/photo-1496217590455-aa63a8350eea?w=500&q=85" },
  // ── Mexico ────────────────────────────────────────────────────────
  { id:"p40", name:"Fernanda Ríos",      country:"Mexico",     region:"Americas",
    specialty:"Commercial / Telenovela Fashion",
    bio:"Mexico City model and creative director whose bold, colourful editorials celebrate Mexican craft heritage.",
    url:"https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=500&q=85" },
  // ── Argentina ─────────────────────────────────────────────────────
  { id:"p41", name:"Luciana Vega",       country:"Argentina",  region:"Americas",
    specialty:"Evening & Gown",
    bio:"Buenos Aires model known for her statuesque elegance; a regular at South American fashion weeks.",
    url:"https://images.unsplash.com/photo-1548454782-15b189d129ab?w=500&q=85" },
  // ── Turkey ────────────────────────────────────────────────────────
  { id:"p42", name:"Yasemin Arslan",     country:"Turkey",     region:"Middle East",
    specialty:"Fusion Editorial",
    bio:"Istanbul model who blends East-West aesthetics, fronting campaigns that celebrate Turkish fashion heritage.",
    url:"https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=500&q=85" },
  // ── UAE ───────────────────────────────────────────────────────────
  { id:"p43", name:"Layla Al-Hassan",    country:"UAE",        region:"Middle East",
    specialty:"Luxury & Occasion Wear",
    bio:"Dubai-based model and luxury brand consultant whose work represents the modern Middle Eastern aesthetic.",
    url:"https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=500&q=85" },
  // ── Indonesia ─────────────────────────────────────────────────────
  { id:"p44", name:"Dewi Rahayu",        country:"Indonesia",  region:"Asia",
    specialty:"Batik & Contemporary",
    bio:"Jakarta model whose editorial work celebrates the richness of Indonesian batik in contemporary fashion.",
    url:"https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=500&q=85" },
  // ── Thailand ──────────────────────────────────────────────────────
  { id:"p45", name:"Praewa Suthat",      country:"Thailand",   region:"Asia",
    specialty:"Resort & Tropical",
    bio:"Bangkok editorial model who captures the elegance of Thai fashion for both local and international audiences.",
    url:"https://images.unsplash.com/photo-1547496502-affa22d38842?w=500&q=85" },
  // ── Philippines ───────────────────────────────────────────────────
  { id:"p46", name:"Rica Santos",        country:"Philippines",region:"Asia",
    specialty:"Commercial & Runway",
    bio:"Manila-based model who brings warmth and vibrancy to campaigns spanning fashion, beauty, and lifestyle.",
    url:"https://images.unsplash.com/photo-1619895862022-09114b41f16f?w=500&q=85" },
  // ── Vietnam ───────────────────────────────────────────────────────
  { id:"p47", name:"Linh Phuong",        country:"Vietnam",    region:"Asia",
    specialty:"Ao Dai & Contemporary",
    bio:"Ho Chi Minh City model who champions Vietnamese ao dai on international editorial stages.",
    url:"https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=500&q=85" },
  // ── Egypt ─────────────────────────────────────────────────────────
  { id:"p48", name:"Nadia El-Masry",     country:"Egypt",      region:"Middle East",
    specialty:"Resort & Occasion Wear",
    bio:"Cairo-born model whose Mediterranean-inspired editorial work is synonymous with timeless elegance.",
    url:"https://images.unsplash.com/photo-1551803091-e20673f15770?w=500&q=85" },
  // ── Greece ────────────────────────────────────────────────────────
  { id:"p49", name:"Dimitra Papadakis",  country:"Greece",     region:"Europe",
    specialty:"Resort & Mediterranean",
    bio:"Athens model whose sun-drenched editorial work captures the spirit of Greek island luxury.",
    url:"https://images.unsplash.com/photo-1614201061439-c86c1de7c37a?w=500&q=85" },
  // ── Netherlands ───────────────────────────────────────────────────
  { id:"p50", name:"Fleur van den Berg", country:"Netherlands",region:"Europe",
    specialty:"Sustainable Fashion",
    bio:"Amsterdam-based sustainable fashion advocate whose campaigns champion ethical design and circular fashion.",
    url:"https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&q=85" },
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
  Jacket:     "bg-amber-500/20 text-amber-300 border-amber-500/30",
  Jackets:    "bg-amber-500/20 text-amber-300 border-amber-500/30",
  Set:        "bg-violet-500/20 text-violet-300 border-violet-500/30",
  Casual:     "bg-sky-500/20 text-sky-300 border-sky-500/30",
  Men:        "bg-neutral-500/20 text-neutral-300 border-neutral-500/30",
  Formal:     "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Dress:      "bg-rose-500/20 text-rose-300 border-rose-500/30",
  Dresses:    "bg-rose-500/20 text-rose-300 border-rose-500/30",
  Ethnic:     "bg-orange-500/20 text-orange-300 border-orange-500/30",
  Shirts:     "bg-blue-500/20 text-blue-300 border-blue-500/30",
  Bottoms:    "bg-teal-500/20 text-teal-300 border-teal-500/30",
  Knitwear:   "bg-purple-500/20 text-purple-300 border-purple-500/30",
  Activewear: "bg-lime-500/20 text-lime-300 border-lime-500/30",
  Evening:    "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
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
/* ─── HELPERS ─────────────────────────────────────────────────── */
/** Download any image src (data-URI or URL) as a PNG file */
function downloadImage(src, filename = 'design.png') {
  if (src.startsWith('data:')) {
    const a = document.createElement('a');
    a.href = src;
    a.download = filename;
    a.click();
  } else {
    // Cross-origin URL — fetch and re-download as blob
    fetch(src)
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 5000);
      })
      .catch(() => { window.open(src, '_blank'); });
  }
}

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
  const [copySpecPulse, setCopySpecPulse] = useState(false);
  const [showBeforeAfter, setShowBeforeAfter] = useState(false);
  const [collectionSubTab, setCollectionSubTab] = useState('saved'); // 'saved' | 'garments' | 'models' | 'people'
  const [garmentCatFilter, setGarmentCatFilter] = useState('All');
  const [modelGenderFilter, setModelGenderFilter] = useState('All'); // 'All' | 'Female' | 'Male'
  const [peopleRegionFilter, setPeopleRegionFilter] = useState('All');
  const [peopleSearch, setPeopleSearch] = useState('');
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

  const handleCopySpec = () => {
    if (!designJob.spec) return;
    const text = JSON.stringify(designJob.spec, null, 2);
    navigator.clipboard.writeText(text).then(() => {
      setCopySpecPulse(true);
      setTimeout(() => setCopySpecPulse(false), 1600);
    });
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

      const res = await fetch('/api/try-on', {
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
      setTryOnJob({ status: 'failed', resultImage: null, statusMsg: 'Connection error — please try again.' });
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
              {/* Copy spec / Close row */}
              <div className="flex gap-2.5">
                <button
                  onClick={handleCopySpec}
                  className={`flex-1 py-3 rounded-xl text-sm font-semibold transition-all border active:scale-[.98] flex items-center justify-center gap-2
                    ${copySpecPulse
                      ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                      : 'bg-white/5 border-white/10 text-neutral-300 hover:bg-white/10 hover:text-white'}`}
                >
                  {copySpecPulse ? <><Check size={13} /> Copied!</> : <><Copy size={13} /> Copy Spec</>}
                </button>
                <button
                  onClick={() => setShowTechPack(false)}
                  className="flex-1 bg-white text-black py-3 rounded-xl text-sm font-semibold hover:bg-neutral-100 active:scale-[.98] transition-all"
                >
                  Close
                </button>
              </div>
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
                      { icon: Download,  title: "Download",   action: () => downloadImage(designJob.image, 'studio-ai-design.png') },
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
                    {/* Before/After toggle — only shown once result is ready */}
                    {tryOnJob.resultImage && personImage && (
                      <button
                        onClick={() => setShowBeforeAfter(v => !v)}
                        title="Toggle Before / After"
                        className={`ml-auto flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-lg border transition-all
                          ${showBeforeAfter
                            ? 'bg-violet-500/20 border-violet-500/40 text-violet-300'
                            : 'bg-white/5 border-white/10 text-neutral-500 hover:text-white hover:border-white/20'}`}
                      >
                        <Columns2 size={11} /> Before / After
                      </button>
                    )}
                  </div>

                  {/* ── Before / After side-by-side ── */}
                  {showBeforeAfter && tryOnJob.resultImage && personImage ? (
                    <div className="flex gap-2 rounded-2xl overflow-hidden border border-white/8 bg-black/30">
                      <div className="flex-1 relative min-h-[220px]">
                        <img src={personImage} className="w-full h-full object-cover" alt="Before" />
                        <div className="absolute bottom-0 inset-x-0 bg-black/60 backdrop-blur-sm py-1.5 text-center">
                          <span className="text-[10px] font-bold text-white/70 uppercase tracking-widest">Before</span>
                        </div>
                      </div>
                      <div className="flex-1 relative min-h-[220px]">
                        <img src={tryOnJob.resultImage} className="w-full h-full object-cover" alt="After" />
                        <div className="absolute bottom-0 inset-x-0 bg-violet-600/70 backdrop-blur-sm py-1.5 text-center">
                          <span className="text-[10px] font-bold text-white uppercase tracking-widest">After</span>
                        </div>
                        <button
                          onClick={() => setExpandedImage(tryOnJob.resultImage)}
                          className="absolute top-2 right-2 w-7 h-7 bg-black/60 backdrop-blur rounded-lg text-white border border-white/10 flex items-center justify-center"
                        >
                          <Maximize2 size={11} />
                        </button>
                      </div>
                    </div>
                  ) : (
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
                  )}

                  {/* Download try-on result */}
                  {tryOnJob.resultImage && (
                    <button
                      onClick={() => downloadImage(tryOnJob.resultImage, 'studio-ai-tryon.png')}
                      className="w-full flex items-center justify-center gap-2 text-xs font-semibold text-neutral-400 hover:text-white bg-white/4 border border-white/8 hover:border-white/16 py-2 rounded-xl transition-all"
                    >
                      <Download size={12} /> Download Result
                    </button>
                  )}
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
          <div className="space-y-6 anim-fade-up">

            {/* ── Collection Page Header ───────────────────────────── */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Collection</h2>
                <p className="text-xs text-neutral-600 mt-1">
                  {collectionSubTab === 'saved'    && `${savedDesigns.length} design${savedDesigns.length !== 1 ? 's' : ''} saved locally`}
                  {collectionSubTab === 'garments' && `${GARMENT_SAMPLES.length} garment samples · open-source photos`}
                  {collectionSubTab === 'models'   && `${FEMALE_MODELS.length + MALE_MODELS.length} model photos · ${FEMALE_MODELS.length} female · ${MALE_MODELS.length} male`}
                  {collectionSubTab === 'people'   && `${FASHION_MODELS.length} editorial models · ${Array.from(new Set(FASHION_MODELS.map(m=>m.region))).length} regions · fictional profiles`}
                </p>
              </div>
              <button
                onClick={() => setActiveTab('design')}
                className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white bg-white/4 border border-white/8 hover:border-white/16 px-3.5 py-2 rounded-xl transition-all"
              >
                <Plus size={11} /> New Design
              </button>
            </div>

            {/* ── Sub-tab pills ────────────────────────────────────── */}
            <div className="flex flex-wrap items-center gap-2 bg-white/3 border border-white/7 rounded-2xl p-1.5 w-fit">
              {[
                { id: 'saved',    label: `Saved Designs${savedDesigns.length > 0 ? ` (${savedDesigns.length})` : ''}` },
                { id: 'garments', label: `Garment Samples (${GARMENT_SAMPLES.length})` },
                { id: 'models',   label: `Model Photos (${FEMALE_MODELS.length + MALE_MODELS.length})` },
                { id: 'people',   label: `Models Directory (${FASHION_MODELS.length})` },
              ].map(st => (
                <button
                  key={st.id}
                  onClick={() => setCollectionSubTab(st.id)}
                  className={`px-4 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    collectionSubTab === st.id
                      ? 'bg-violet-600 text-white shadow'
                      : 'text-neutral-500 hover:text-neutral-300'
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>

            {/* ════════════════════════════════════════════════════
                SUB-TAB: SAVED DESIGNS
            ═══════════════════════════════════════════════════ */}
            {collectionSubTab === 'saved' && (
              savedDesigns.length === 0 ? (
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
                            <button onClick={() => downloadImage(design.image, `studio-ai-design-${design.id}.png`)} title="Download" className="w-7 h-7 text-neutral-700 hover:text-sky-400 hover:bg-sky-400/10 rounded-lg flex items-center justify-center transition-all"><Download size={12} /></button>
                            <button onClick={() => handleGenerateDesign(design.prompt)} title="Remix" className="w-7 h-7 text-neutral-700 hover:text-violet-400 hover:bg-violet-400/10 rounded-lg flex items-center justify-center transition-all"><RefreshCw size={12} /></button>
                            <button onClick={() => { StorageService.deleteDesign(design.id); setSavedDesigns(StorageService.getCollections()); }} title="Delete" className="w-7 h-7 text-neutral-800 hover:text-red-400 hover:bg-red-400/10 rounded-lg flex items-center justify-center transition-all"><Trash2 size={12} /></button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            )}

            {/* ════════════════════════════════════════════════════
                SUB-TAB: GARMENT SAMPLES (100 items)
            ═══════════════════════════════════════════════════ */}
            {collectionSubTab === 'garments' && (() => {
              const gsCats = ['All', ...Array.from(new Set(GARMENT_SAMPLES.map(g => g.category)))];
              const gsFiltered = garmentCatFilter === 'All' ? GARMENT_SAMPLES : GARMENT_SAMPLES.filter(g => g.category === garmentCatFilter);
              return (
                <div className="space-y-5">
                  {/* Category filter pills */}
                  <div className="flex flex-wrap gap-2">
                    {gsCats.map(cat => (
                      <button
                        key={cat}
                        onClick={() => setGarmentCatFilter(cat)}
                        className={`px-3 py-1 rounded-lg text-[11px] font-semibold border transition-all ${
                          garmentCatFilter === cat
                            ? 'bg-violet-600 border-violet-600 text-white'
                            : 'bg-white/3 border-white/8 text-neutral-500 hover:text-neutral-300 hover:border-white/20'
                        }`}
                      >
                        {cat} {cat !== 'All' ? `(${GARMENT_SAMPLES.filter(g => g.category === cat).length})` : `(${GARMENT_SAMPLES.length})`}
                      </button>
                    ))}
                  </div>

                  {/* Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    {gsFiltered.map(g => (
                      <div
                        key={g.id}
                        className="bg-white/3 border border-white/7 rounded-2xl overflow-hidden group cursor-pointer card-hover"
                        onClick={() => setExpandedImage(g.url)}
                      >
                        <div className="aspect-[3/4] overflow-hidden bg-neutral-950 relative">
                          <img
                            src={g.url}
                            alt={g.label}
                            loading="lazy"
                            className="w-full h-full object-cover group-hover:scale-[1.05] transition-transform duration-500"
                            onError={e => { e.currentTarget.src = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=60'; }}
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                            <Maximize2 size={16} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                        <div className="p-2.5">
                          <p className="text-[11px] text-neutral-300 font-medium truncate">{g.label}</p>
                          <span className={`inline-block mt-1 text-[9px] px-1.5 py-0.5 rounded-md border font-semibold ${CAT_COLORS[g.category] || 'bg-neutral-500/20 text-neutral-300 border-neutral-500/30'}`}>
                            {g.category}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            {/* ════════════════════════════════════════════════════
                SUB-TAB: MODEL PHOTOS (50F + 20M)
            ═══════════════════════════════════════════════════ */}
            {collectionSubTab === 'models' && (() => {
              const allModels = [
                ...FEMALE_MODELS.map(m => ({ ...m, gender: 'Female' })),
                ...MALE_MODELS.map(m => ({ ...m, gender: 'Male' })),
              ];
              const filteredModels = modelGenderFilter === 'All' ? allModels
                : allModels.filter(m => m.gender === modelGenderFilter);
              return (
                <div className="space-y-5">
                  {/* Gender filter */}
                  <div className="flex items-center gap-2">
                    {['All', 'Female', 'Male'].map(g => (
                      <button
                        key={g}
                        onClick={() => setModelGenderFilter(g)}
                        className={`px-4 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                          modelGenderFilter === g
                            ? 'bg-violet-600 border-violet-600 text-white'
                            : 'bg-white/3 border-white/8 text-neutral-500 hover:text-neutral-300 hover:border-white/20'
                        }`}
                      >
                        {g === 'All' ? `All (${allModels.length})` : g === 'Female' ? `Female (${FEMALE_MODELS.length})` : `Male (${MALE_MODELS.length})`}
                      </button>
                    ))}
                  </div>

                  {/* Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    {filteredModels.map(m => (
                      <div
                        key={m.id}
                        className="bg-white/3 border border-white/7 rounded-2xl overflow-hidden group cursor-pointer card-hover"
                        onClick={() => setExpandedImage(m.url)}
                      >
                        <div className="aspect-[3/4] overflow-hidden bg-neutral-950 relative">
                          <img
                            src={m.url}
                            alt={m.label}
                            loading="lazy"
                            className="w-full h-full object-cover group-hover:scale-[1.05] transition-transform duration-500"
                            onError={e => { e.currentTarget.src = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=60'; }}
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                            <Maximize2 size={16} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                          {/* Gender badge */}
                          <span className={`absolute top-2 left-2 text-[9px] px-1.5 py-0.5 rounded-md font-bold border ${
                            m.gender === 'Female'
                              ? 'bg-rose-500/25 text-rose-300 border-rose-500/30'
                              : 'bg-sky-500/25 text-sky-300 border-sky-500/30'
                          }`}>{m.gender}</span>
                        </div>
                        <div className="p-2.5">
                          <p className="text-[11px] text-neutral-300 font-medium truncate">{m.label}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            {/* ════════════════════════════════════════════════════
                SUB-TAB: MODELS DIRECTORY — 50 fictional editorial
            ═══════════════════════════════════════════════════ */}
            {collectionSubTab === 'people' && (() => {
              const allRegions = ['All', ...Array.from(new Set(FASHION_MODELS.map(m => m.region)))].sort((a,b) => a === 'All' ? -1 : b === 'All' ? 1 : a.localeCompare(b));
              const q = peopleSearch.toLowerCase().trim();
              const filtered = FASHION_MODELS.filter(m => {
                const matchRegion = peopleRegionFilter === 'All' || m.region === peopleRegionFilter;
                const matchSearch = !q || m.name.toLowerCase().includes(q) || m.country.toLowerCase().includes(q) || m.specialty.toLowerCase().includes(q);
                return matchRegion && matchSearch;
              });
              const REGION_COLORS = {
                Americas:     'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
                Europe:       'bg-blue-500/20 text-blue-300 border-blue-500/30',
                Asia:         'bg-rose-500/20 text-rose-300 border-rose-500/30',
                Africa:       'bg-amber-500/20 text-amber-300 border-amber-500/30',
                'Middle East':'bg-orange-500/20 text-orange-300 border-orange-500/30',
                Oceania:      'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
              };
              return (
                <div className="space-y-5">
                  {/* Search + region filters */}
                  <div className="flex flex-col sm:flex-row gap-3">
                    {/* Search box */}
                    <div className="relative flex-1 max-w-xs">
                      <input
                        type="text"
                        placeholder="Search by name, country, specialty…"
                        value={peopleSearch}
                        onChange={e => setPeopleSearch(e.target.value)}
                        className="w-full bg-white/4 border border-white/10 rounded-xl px-3 py-2 text-xs text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500/50 focus:bg-white/6 transition-all"
                      />
                      {peopleSearch && (
                        <button
                          onClick={() => setPeopleSearch('')}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-neutral-600 hover:text-neutral-300 transition-colors"
                        >
                          <X size={11} />
                        </button>
                      )}
                    </div>
                    {/* Region pills */}
                    <div className="flex flex-wrap gap-1.5">
                      {allRegions.map(r => (
                        <button
                          key={r}
                          onClick={() => setPeopleRegionFilter(r)}
                          className={`px-3 py-1 rounded-lg text-[11px] font-semibold border transition-all ${
                            peopleRegionFilter === r
                              ? 'bg-violet-600 border-violet-600 text-white'
                              : 'bg-white/3 border-white/8 text-neutral-500 hover:text-neutral-300 hover:border-white/20'
                          }`}
                        >
                          {r === 'All' ? `All (${FASHION_MODELS.length})` : r}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Result count */}
                  {q || peopleRegionFilter !== 'All' ? (
                    <p className="text-[11px] text-neutral-600">
                      Showing {filtered.length} of {FASHION_MODELS.length} models
                      {peopleRegionFilter !== 'All' && ` · ${peopleRegionFilter}`}
                      {q && ` · "${peopleSearch}"`}
                    </p>
                  ) : null}

                  {/* Cards grid */}
                  {filtered.length === 0 ? (
                    <div className="bg-white/2 border border-white/5 rounded-2xl py-14 text-center">
                      <p className="text-sm text-neutral-600">No models match your search.</p>
                      <button onClick={() => { setPeopleSearch(''); setPeopleRegionFilter('All'); }}
                        className="mt-3 text-xs text-violet-400 hover:text-violet-300 transition-colors">
                        Clear filters
                      </button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5">
                      {filtered.map(m => (
                        <div
                          key={m.id}
                          className="bg-white/3 border border-white/7 rounded-2xl overflow-hidden flex flex-col group card-hover cursor-pointer"
                          onClick={() => setExpandedImage(m.url)}
                        >
                          {/* Photo */}
                          <div className="aspect-[3/4] overflow-hidden bg-neutral-950 relative">
                            <img
                              src={m.url}
                              alt={m.name}
                              loading="lazy"
                              className="w-full h-full object-cover object-top group-hover:scale-[1.05] transition-transform duration-500"
                              onError={e => { e.currentTarget.src = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&q=60'; }}
                            />
                            {/* Hover overlay */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                            <div className="absolute bottom-2.5 left-2.5 right-2.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <p className="text-[10px] text-white/80 leading-relaxed line-clamp-3">{m.bio}</p>
                            </div>
                            {/* Region badge */}
                            <span className={`absolute top-2 right-2 text-[9px] px-1.5 py-0.5 rounded-md font-bold border backdrop-blur-sm ${REGION_COLORS[m.region] || 'bg-neutral-500/25 text-neutral-300 border-neutral-500/30'}`}>
                              {m.region}
                            </span>
                            {/* Expand icon */}
                            <div className="absolute top-2 left-2 w-6 h-6 bg-black/50 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                              <Maximize2 size={10} className="text-white" />
                            </div>
                          </div>
                          {/* Card info */}
                          <div className="p-3 flex flex-col gap-1.5">
                            <p className="text-[12px] text-white font-semibold leading-tight truncate">{m.name}</p>
                            <div className="flex items-center gap-1 flex-wrap">
                              <span className="text-[10px] text-neutral-500">🌍</span>
                              <span className="text-[10px] text-neutral-400 font-medium">{m.country}</span>
                            </div>
                            <span className="text-[9px] text-violet-400 font-semibold truncate">{m.specialty}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })()}

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
