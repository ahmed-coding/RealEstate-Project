import React, { useEffect, useState } from 'react';
import { getFavorites, deleteFavorite } from '../api/favorite';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getFavorites()
      .then(setFavorites)
      .catch(() => setError('Failed to load favorites'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse">Loading favorites...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!favorites.length) return <div>No favorites found.</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">My Favorites</h1>
      <ul className="grid gap-4 md:grid-cols-2">
        {favorites.map((fav) => (
          <li key={fav.id} className="bg-white dark:bg-gray-800 rounded shadow p-4 flex flex-col">
            <div className="flex-1">
              <h2 className="font-semibold text-lg mb-2">{fav.title || 'Untitled Property'}</h2>
              <p className="text-sm text-gray-500">{fav.address || 'No address provided'}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <button onClick={() => deleteFavorite(fav.id).then(() => setFavorites(favorites.filter(f => f.id !== fav.id)))} className="text-red-500">Remove</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
