/**
 * Offline report queue — IndexedDB-backed pending uploads.
 * Never claims a report was uploaded if it was not.
 */
const DB_NAME = 'sangam-offline';
const STORE = 'pending_reports';
const VERSION = 1;

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function queueReport(payload) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    const store = tx.objectStore(STORE);
    const record = {
      ...payload,
      queuedAt: new Date().toISOString(),
      status: 'pending',
    };
    const req = store.add(record);
    req.onsuccess = () => resolve({ id: req.result, ...record });
    req.onerror = () => reject(req.error);
  });
}

export async function listPendingReports() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly');
    const req = tx.objectStore(STORE).getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

export async function removePendingReport(id) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    const req = tx.objectStore(STORE).delete(id);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

export function isOnline() {
  return typeof navigator === 'undefined' ? true : navigator.onLine;
}
