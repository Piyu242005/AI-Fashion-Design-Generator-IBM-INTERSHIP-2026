const STORAGE_KEY = 'ai_fashion_collections';

function readCollections() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error('Invalid collection data');
    return parsed.filter(item => item && typeof item === 'object');
  } catch (error) {
    console.warn('[AI Fashion Studio] Resetting invalid collection storage:', error);
    try { window.localStorage.removeItem(STORAGE_KEY); } catch {}
    return [];
  }
}

function writeCollections(collections) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(collections));
    return true;
  } catch (error) {
    console.warn('[AI Fashion Studio] Could not save collection:', error);
    return false;
  }
}

export const StorageService = Object.freeze({
  getCollections: readCollections,
  saveDesign(design) {
    const collections = readCollections();
    const saved = { ...design, id: Date.now(), isTracking: false };
    writeCollections([saved, ...collections]);
    return saved;
  },
  deleteDesign(id) {
    writeCollections(readCollections().filter(item => item.id !== id));
  },
  toggleTrack(id) {
    const updated = readCollections().map(item =>
      item.id === id ? { ...item, isTracking: !item.isTracking } : item
    );
    writeCollections(updated);
    return updated;
  },
  clear() {
    try { window.localStorage.removeItem(STORAGE_KEY); } catch {}
  },
});
