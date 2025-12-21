import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  projectId: "bbl-mit-hack-2025",
  appId: "1:429970492504:web:f941b968b7a2e7ffc10e2d",
  storageBucket: "bbl-mit-hack-2025.firebasestorage.app",
  apiKey: "AIzaSyC7GAV2lq1arIjPHT_GvQMfl8XtuyGU8-M",
  authDomain: "bbl-mit-hack-2025.firebaseapp.com",
  messagingSenderId: "429970492504",
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
