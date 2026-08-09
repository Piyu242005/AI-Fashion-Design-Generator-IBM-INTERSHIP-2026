import React, { useState, useRef, useEffect } from 'react';
import { 
  Sparkles, Image as ImageIcon, Loader2, Download, 
  Scissors, ShoppingBag, User, Upload, Layers, Trash2, 
  Maximize2, RefreshCw, X, Camera, Palette, Leaf, FileText, Bell, BellRing, Activity
} from 'lucide-react';

// --- CONFIGURATION ---
// Put your Gemini API Key here for production. 
// If left empty, the app uses Portfolio Mock Mode to ensure it always works for demos!
const API_KEY = ""; 

// --- UTILITY & STORAGE SERVICES ---
const StorageService = {
  getCollections: () => JSON.parse(localStorage.getItem('ai_fashion_collections') || '[]'),
  saveDesign: (design) => {
    const collections = StorageService.getCollections();
    const newDesign = { ...design, id: Date.now(), isTracking: false };
    localStorage.setItem('ai_fashion_collections', JSON.stringify([newDesign, ...collections]));
    return newDesign;
  },
  deleteDesign: (id) => {
    const collections = StorageService.getCollections();
    localStorage.setItem('ai_fashion_collections', JSON.stringify(collections.filter(d => d.id !== id)));
  },
  toggleTrack: (id) => {
    const collections = StorageService.getCollections();
    const updated = collections.map(d => d.id === id ? { ...d, isTracking: !d.isTracking } : d);
    localStorage.setItem('ai_fashion_collections', JSON.stringify(updated));
    return updated;
  }
};

const cleanJSON = (text) => {
  try {
    const match = text.match(/```(?:json)?\n([\s\S]*?)\n```/);
    return match ? match[1] : text;
  } catch (e) {
    return text;
  }
};

// --- CORE AI SERVICES (WITH MOCK FALLBACKS FOR PORTFOLIO) ---
const FashionIntelligenceService = {
  async extractSpecification(prompt) {
    if (!API_KEY) return this.mockSpec(prompt);
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${API_KEY}`;
      const payload = { 
        contents: [{ parts: [{ text: `Extract fashion details to JSON: ${prompt}. Schema: {"category":"", "fabric":"", "colors":["hex codes"], "sustainability_score": 0-100, "budget": {"maximum": number}}` }] }], 
        generationConfig: { responseMimeType: "application/json" } 
      };
      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      return JSON.parse(cleanJSON(data.candidates[0].content.parts[0].text));
    } catch (e) {
      return this.mockSpec(prompt);
    }
  },
  mockSpec: (prompt) => ({
    category: prompt.includes("kurta") ? "Kurta" : "Jacket",
    fabric: "Organic Cotton",
    colors: ["#0f172a", "#334155", "#94a3b8"],
    sustainability_score: 85,
    budget: { maximum: 2999 },
    optimized_image_prompt: prompt
  })
};

const ImageGenerationService = {
  async generate(optimizedPrompt) {
    if (!API_KEY) return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80"; // Fallback Image
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${API_KEY}`;
      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ instances: { prompt: optimizedPrompt } }) });
      const data = await res.json();
      if (data.predictions && data.predictions[0]) return `data:image/png;base64,${data.predictions[0].bytesBase64Encoded}`;
      throw new Error();
    } catch (e) {
      return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80";
    }
  }
};

const ProductSearchService = {
  async searchSimilarProducts(spec) {
    return [
      { name: "Minimalist " + spec.category, price: 1499, platform: "Myntra", similarity_score: 92 },
      { name: "Premium " + spec.fabric + " Blend", price: 2199, platform: "Ajio", similarity_score: 88 },
      { name: "Urban Streetwear Concept", price: 2899, platform: "Tata CLiQ", similarity_score: 85 }
    ];
  }
};

const VirtualTryOnService = {
  async processTryOn(personImage, garmentImage) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const pImg = new Image();
        const gImg = new Image();
        pImg.crossOrigin = "anonymous";
        gImg.crossOrigin = "anonymous";
        
        pImg.onload = () => {
          canvas.width = pImg.width; canvas.height = pImg.height;
          ctx.drawImage(pImg, 0, 0, pImg.width, pImg.height);
          gImg.onload = () => {
            ctx.globalAlpha = 0.85;
            const w = pImg.width * 0.7; 
            const h = (gImg.height / gImg.width) * w;
            ctx.drawImage(gImg, (pImg.width - w) / 2, pImg.height * 0.2, w, h);
            resolve({ resultImage: canvas.toDataURL('image/png') });
          };
          gImg.src = garmentImage;
        };
        pImg.src = personImage;
      }, 2500); 
    });
  }
};

// --- MOCK RUNWAY DATA ---
const runwayData = [
  { id: 1, prompt: "Cyberpunk streetwear jacket with neon accents", image: "https://images.unsplash.com/photo-1550614000-4b95dd1a6c8e?w=800&q=80" },
  { id: 2, prompt: "Indo-western fusion lehenga, minimalist beige", image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80" },
  { id: 3, prompt: "Sustainable bamboo fabric summer dress", image: "https://images.unsplash.com/photo-1515347619362-e5fdffdc8fb8?w=800&q=80" }
];

// --- MAIN APP COMPONENT ---
export default function App() {
  const [activeTab, setActiveTab] = useState('runway');
  const [prompt, setPrompt] = useState("");
  const [designJob, setDesignJob] = useState({ status: 'idle', spec: null, image: null, products: [] });
  
  // Modals & Overlays
  const [expandedImage, setExpandedImage] = useState(null); 
  const [showTechPack, setShowTechPack] = useState(false);
  
  // Try-On State
  const [personImage, setPersonImage] = useState(null);
  const [tryOnJob, setTryOnJob] = useState({ status: 'idle', resultImage: null });
  const [bodyAnalysis, setBodyAnalysis] = useState(null);
  const fileInputRef = useRef(null);

  // Collections State
  const [savedDesigns, setSavedDesigns] = useState([]);

  useEffect(() => { setSavedDesigns(StorageService.getCollections()); }, []);

  // Actions
  const handleGenerateDesign = async (overridePrompt = null) => {
    const targetPrompt = overridePrompt || prompt;
    if (!targetPrompt.trim()) return;
    
    setPrompt(targetPrompt);
    if(activeTab !== 'design') setActiveTab('design');
    setDesignJob({ status: 'processing', spec: null, image: null, products: [] });
    
    try {
      const spec = await FashionIntelligenceService.extractSpecification(targetPrompt);
      const [image, products] = await Promise.all([
        ImageGenerationService.generate(spec.optimized_image_prompt),
        ProductSearchService.searchSimilarProducts(spec)
      ]);
      setDesignJob({ status: 'completed', spec, image, products, prompt: targetPrompt });
    } catch (error) {
      setDesignJob({ status: 'failed', spec: null, image: null, products: [] });
    }
  };

  const handleVisualSearch = () => {
    setPrompt("Reverse Engineered: A navy blue velvet blazer with intricate gold zari embroidery on the lapel, formal wear, Indian style.");
  };

  const handlePersonUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setPersonImage(ev.target.result);
        setBodyAnalysis(null);
        setTimeout(() => setBodyAnalysis({ shape: 'Athletic/Rectangle', match: 92, tips: 'Structured shoulders and cinched waist will compliment your proportions.' }), 2000);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleTryOn = async () => {
    if (!personImage || !designJob.image) return;
    setTryOnJob({ status: 'processing', resultImage: null });
    const result = await VirtualTryOnService.processTryOn(personImage, designJob.image);
    setTryOnJob({ status: 'completed', resultImage: result.resultImage });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-neutral-100 font-sans selection:bg-neutral-800 pb-12">
      
      {/* Overlays */}
      {expandedImage && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-md flex items-center justify-center p-4">
          <button onClick={() => setExpandedImage(null)} className="absolute top-6 right-6 text-neutral-400 hover:text-white bg-neutral-900/50 p-2 rounded-full"><X size={24} /></button>
          <img src={expandedImage} alt="Expanded Render" className="max-w-full max-h-full rounded-lg object-contain shadow-2xl" />
        </div>
      )}

      {showTechPack && designJob.spec && (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0a0a0a] border border-neutral-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b border-neutral-900 bg-[#050505]">
              <h2 className="font-semibold flex items-center gap-2"><FileText size={18}/> Manufacturing Tech Pack</h2>
              <button onClick={() => setShowTechPack(false)} className="text-neutral-500 hover:text-white"><X size={20}/></button>
            </div>
            <div className="p-6 space-y-6 text-sm text-neutral-300">
              <div className="grid grid-cols-2 gap-4">
                <div><span className="text-neutral-500 block text-xs">Primary Fabric</span>{designJob.spec.fabric || 'Unknown'}</div>
                <div><span className="text-neutral-500 block text-xs">Category</span>{designJob.spec.category || 'Apparel'}</div>
                <div><span className="text-neutral-500 block text-xs">Color Codes (HEX)</span>{designJob.spec.colors?.join(', ') || 'N/A'}</div>
                <div><span className="text-neutral-500 block text-xs">Target Cost Price</span>₹{(designJob.spec.budget?.maximum * 0.4).toFixed(0) || 'N/A'} (Estimated)</div>
              </div>
              <div className="bg-neutral-900/50 p-4 rounded-xl border border-neutral-800">
                <h4 className="font-medium text-white mb-2">Construction Notes</h4>
                <ul className="list-disc pl-4 space-y-1 text-xs text-neutral-400">
                  <li>Ensure standard 1.5cm seam allowance.</li>
                  <li>Use eco-friendly dyes to maintain {designJob.spec.sustainability_score || 80}/100 sustainability score.</li>
                  <li>Derived from AI Concept Prompt: {designJob.prompt}</li>
                </ul>
              </div>
              <button onClick={() => setShowTechPack(false)} className="w-full bg-white text-black py-2 rounded-lg font-medium">Download PDF (Simulated)</button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="bg-[#0a0a0a] border-b border-neutral-900 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-neutral-100 text-black p-2 rounded-lg"><Scissors size={18} /></div>
            <h1 className="text-lg font-semibold tracking-tight text-white hidden sm:block">AI Fashion Studio</h1>
          </div>
          <div className="flex gap-1 bg-neutral-900/50 p-1 rounded-xl border border-neutral-800 overflow-x-auto">
            {[
              { id: 'runway', label: 'Runway', icon: Activity },
              { id: 'design', label: 'Studio', icon: Sparkles },
              { id: 'tryon', label: 'Try-On', icon: User },
              { id: 'collection', label: `Saved (${savedDesigns.length})`, icon: Layers }
            ].map(tab => (
              <button
                key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-neutral-800 text-white shadow-sm' : 'text-neutral-500 hover:text-neutral-300'}`}
              ><tab.icon size={14} /> {tab.label}</button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 mt-4">
        
        {/* THE RUNWAY */}
        {activeTab === 'runway' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center max-w-2xl mx-auto mb-10">
              <h2 className="text-3xl font-bold text-white mb-4">Discover Inspiration</h2>
              <p className="text-neutral-400">Explore community-generated concepts. Find a design you love and remix it in the AI Studio.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {runwayData.map((item) => (
                <div key={item.id} className="bg-[#0a0a0a] border border-neutral-900 rounded-2xl overflow-hidden group">
                  <div className="h-80 w-full relative overflow-hidden bg-[#050505]">
                    <img src={item.image} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-5">
                      <p className="text-sm font-medium text-white mb-3 line-clamp-2">{item.prompt}</p>
                      <button onClick={() => handleGenerateDesign(item.prompt)} className="w-full bg-white/20 backdrop-blur-md text-white border border-white/30 py-2 rounded-xl text-xs font-semibold hover:bg-white hover:text-black transition-colors">
                        Remix Design
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DESIGN STUDIO */}
        {activeTab === 'design' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
            <section className="lg:col-span-4 space-y-6">
              <div className="bg-[#0a0a0a] rounded-2xl p-6 border border-neutral-900 shadow-2xl sticky top-24">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-medium text-neutral-200">Design Parameters</h2>
                  <button onClick={handleVisualSearch} className="text-neutral-500 hover:text-white flex items-center gap-1 text-xs bg-neutral-900 px-2 py-1 rounded-md" title="Visual Search (Upload Image)">
                    <Camera size={14}/> Image to Prompt
                  </button>
                </div>
                <form onSubmit={(e) => handleGenerateDesign()}>
                  <textarea
                    value={prompt} onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe your design (e.g., A minimalist black cotton kurta under ₹3000...)"
                    className="w-full h-32 p-4 bg-[#050505] border border-neutral-800 rounded-xl resize-none focus:outline-none focus:border-neutral-600 mb-4 text-sm text-neutral-300 placeholder:text-neutral-700"
                    required
                  />
                  <button type="submit" disabled={designJob.status === 'processing'} className="w-full bg-neutral-100 text-black py-3 px-4 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-white disabled:opacity-50 transition-all">
                    {designJob.status === 'processing' ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    {designJob.status === 'processing' ? 'Rendering...' : 'Generate Design'}
                  </button>
                </form>
              </div>
            </section>
            
            <section className="lg:col-span-8 space-y-6">
              {designJob.status === 'completed' && designJob.image ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in">
                  
                  {/* GENERATED CONCEPT (Left Side) */}
                  <div className="bg-[#0a0a0a] rounded-2xl border border-neutral-900 overflow-hidden shadow-xl flex flex-col group relative">
                    {/* Action Bar */}
                    <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                      <button onClick={() => handleGenerateDesign()} className="bg-black/60 backdrop-blur-md p-2 rounded-lg text-white hover:bg-black/80 border border-white/10" title="Regenerate"><RefreshCw size={16} /></button>
                      <button onClick={() => {
                        const a = document.createElement('a'); a.href = designJob.image; a.download = 'design.png'; a.click();
                      }} className="bg-black/60 backdrop-blur-md p-2 rounded-lg text-white hover:bg-black/80 border border-white/10" title="Download"><Download size={16} /></button>
                      <button onClick={() => setExpandedImage(designJob.image)} className="bg-black/60 backdrop-blur-md p-2 rounded-lg text-white hover:bg-black/80 border border-white/10" title="Expand"><Maximize2 size={16} /></button>
                    </div>

                    <div className="h-72 w-full relative bg-[#050505]">
                      <img src={designJob.image} alt="Generated" className="w-full h-full object-cover" />
                    </div>
                    
                    {/* Feature Extractors */}
                    <div className="p-4 bg-[#0a0a0a] border-t border-neutral-900 space-y-4">
                      {designJob.spec && (
                        <div className="grid grid-cols-2 gap-2 text-xs">
                           <div className="bg-neutral-900 p-2 rounded-lg border border-neutral-800">
                             <div className="text-neutral-500 mb-1 flex items-center gap-1"><Palette size={12}/> Color Palette</div>
                             <div className="flex gap-1">
                               {designJob.spec.colors?.slice(0,4).map(c => <div key={c} className="w-4 h-4 rounded-full border border-neutral-700" style={{backgroundColor: c}} title={c}></div>) || <span className="text-neutral-400">Extracted</span>}
                             </div>
                           </div>
                           <div className="bg-neutral-900 p-2 rounded-lg border border-neutral-800">
                             <div className="text-neutral-500 mb-1 flex items-center gap-1"><Leaf size={12} className="text-emerald-500"/> Eco-Score</div>
                             <div className="font-semibold text-emerald-400">{designJob.spec.sustainability_score || '80'}/100</div>
                           </div>
                        </div>
                      )}
                      
                      <div className="grid grid-cols-2 gap-2">
                        <button onClick={() => {
                          StorageService.saveDesign({ image: designJob.image, prompt: designJob.prompt, spec: designJob.spec });
                          setSavedDesigns(StorageService.getCollections());
                        }} className="bg-neutral-900 text-neutral-300 border border-neutral-800 py-2.5 rounded-lg text-xs font-medium hover:bg-neutral-800">Save</button>
                        <button onClick={() => setActiveTab('tryon')} className="bg-neutral-200 text-black py-2.5 rounded-lg text-xs font-medium hover:bg-white">Try On</button>
                      </div>
                      <button onClick={() => setShowTechPack(true)} className="w-full bg-neutral-900 text-neutral-400 border border-neutral-800 border-dashed py-2 rounded-lg text-xs font-medium hover:text-white">Generate Tech Pack</button>
                    </div>
                  </div>

                  {/* SMART SHOPPING (Right Side) */}
                  <div className="bg-[#0a0a0a] rounded-2xl border border-neutral-900 shadow-xl flex flex-col">
                     <div className="px-5 py-4 border-b border-neutral-900 flex justify-between text-sm font-medium"><span className="flex items-center gap-2 text-neutral-300"><ShoppingBag size={14}/> Affordable Alternatives</span></div>
                    <div className="p-5 overflow-y-auto max-h-[450px] space-y-3">
                      {designJob.products.map((p, idx) => (
                        <div key={idx} className="bg-[#050505] border border-neutral-900 hover:border-neutral-700 transition-colors rounded-xl p-4 flex flex-col gap-2">
                          <h4 className="text-sm font-medium text-neutral-200 leading-tight">{p.name}</h4>
                          <div className="flex justify-between items-end">
                            <div className="flex flex-col">
                              <span className="text-xs text-neutral-500 mb-0.5">{p.platform}</span>
                              <span className="text-neutral-100 text-sm font-bold">₹{p.price.toLocaleString('en-IN')}</span>
                            </div>
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded-md">{p.similarity_score}% Match</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-[#0a0a0a] rounded-2xl border border-neutral-900 p-12 text-center min-h-[400px] flex flex-col items-center justify-center">
                  {designJob.status === 'processing' ? <Loader2 size={24} className="animate-spin text-neutral-500" /> : <ImageIcon size={24} className="text-neutral-800 mb-4" />}
                </div>
              )}
            </section>
          </div>
        )}

        {/* TRY-ON ROOM */}
        {activeTab === 'tryon' && (
           <div className="bg-[#0a0a0a] rounded-2xl border border-neutral-900 p-8 shadow-2xl animate-in fade-in duration-500">
             <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
               <div className="space-y-3">
                 <h3 className="text-xs font-medium text-neutral-500 uppercase tracking-widest flex items-center justify-between">
                   1. Your Photo
                   {bodyAnalysis === null && personImage && <Loader2 size={12} className="animate-spin text-emerald-400"/>}
                 </h3>
                 <div onClick={() => fileInputRef.current?.click()} className="aspect-[3/4] bg-[#050505] border border-dashed border-neutral-800 hover:border-neutral-600 rounded-xl flex items-center justify-center cursor-pointer overflow-hidden relative">
                   {personImage ? <img src={personImage} className="w-full h-full object-cover" /> : <Upload size={20} className="text-neutral-700" />}
                   <input type="file" ref={fileInputRef} onChange={handlePersonUpload} className="hidden" accept="image/*" />
                 </div>
                 {/* Body ML Mock Result */}
                 {bodyAnalysis && (
                   <div className="bg-neutral-900 border border-neutral-800 p-3 rounded-lg text-xs animate-in fade-in">
                     <strong className="text-emerald-400 block mb-1">Body Analysis Complete</strong>
                     <span className="text-neutral-300">Estimated Type: {bodyAnalysis.shape}</span>
                   </div>
                 )}
               </div>
               
               <div className="space-y-3">
                 <h3 className="text-xs font-medium text-neutral-500 uppercase tracking-widest">2. Garment</h3>
                 <div className="aspect-[3/4] bg-[#050505] border border-neutral-900 rounded-xl flex items-center justify-center overflow-hidden relative">
                   {designJob.image ? <img src={designJob.image} className="w-full h-full object-cover" /> : <p className="text-xs text-neutral-600">Generate a design first</p>}
                 </div>
               </div>
               
               <div className="space-y-3 flex flex-col">
                 <h3 className="text-xs font-medium text-neutral-500 uppercase tracking-widest">3. Result</h3>
                 <div className="flex-1 bg-[#050505] border border-neutral-900 rounded-xl flex items-center justify-center overflow-hidden relative">
                   {tryOnJob.status === 'processing' ? <div className="text-center"><Loader2 className="animate-spin text-neutral-400 mx-auto mb-2" size={24}/> <span className="text-[10px] text-neutral-500">Aligning...</span></div> : tryOnJob.resultImage ? <img src={tryOnJob.resultImage} className="w-full h-full object-cover" /> : <User size={20} className="text-neutral-800" />}
                 </div>
                 <button onClick={handleTryOn} disabled={!personImage || !designJob.image || tryOnJob.status === 'processing'} className="w-full bg-neutral-100 text-black py-3 rounded-xl text-sm font-medium hover:bg-white disabled:opacity-50">Virtual Try-On</button>
               </div>
             </div>
           </div>
        )}

        {/* MY COLLECTION */}
        {activeTab === 'collection' && (
          <div className="space-y-6 animate-in fade-in duration-500">
            <h2 className="text-lg font-medium text-neutral-200">Saved Designs & Price Alerts</h2>
            {savedDesigns.length === 0 ? (
              <div className="bg-[#0a0a0a] p-12 text-center rounded-2xl border border-neutral-900 text-neutral-600 text-sm">No designs saved yet.</div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                {savedDesigns.map(design => (
                  <div key={design.id} className="bg-[#0a0a0a] border border-neutral-900 rounded-xl overflow-hidden flex flex-col">
                    <img src={design.image} className="w-full h-56 object-cover bg-[#050505]" />
                    <div className="p-4 bg-[#0a0a0a] flex-1 flex flex-col justify-between space-y-3">
                      <p className="text-xs text-neutral-400 line-clamp-2">{design.prompt}</p>
                      <div className="flex justify-between items-center pt-2 border-t border-neutral-900">
                         {/* Price Track Alert Simulation */}
                         <button onClick={() => setSavedDesigns(StorageService.toggleTrack(design.id))} className={`flex items-center gap-1 text-[10px] font-medium transition-colors ${design.isTracking ? 'text-emerald-400' : 'text-neutral-600 hover:text-neutral-400'}`}>
                           {design.isTracking ? <BellRing size={12}/> : <Bell size={12}/>}
                           {design.isTracking ? 'Tracking Price' : 'Track Alert'}
                         </button>
                         <div className="flex gap-3">
                           <button onClick={() => setExpandedImage(design.image)} className="text-neutral-500 hover:text-white"><Maximize2 size={14}/></button>
                           <button onClick={() => { StorageService.deleteDesign(design.id); setSavedDesigns(StorageService.getCollections()); }} className="text-neutral-600 hover:text-red-400"><Trash2 size={14}/></button>
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