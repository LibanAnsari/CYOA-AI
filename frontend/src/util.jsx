export const API_BASE_URL = import.meta.env.VITE_API_URL;

// The react app is deployed as a static site so theres no need for a proxy now, this is redundant after the .env changes
// VITE will decide which .env to use during npm run dev it will use .env
// and when we deploy, it will use .env.production, which points to our deployed backend URL