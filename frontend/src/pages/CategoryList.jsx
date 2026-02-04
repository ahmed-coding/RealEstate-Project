import React, { useEffect, useState } from 'react';
import { getCategories } from '../api/category';

export default function CategoryList() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setError('Failed to load categories'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse">Loading categories...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!categories.length) return <div>No categories found.</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Categories</h1>
      <ul className="grid gap-4 md:grid-cols-2">
        {categories.map((cat) => (
          <li key={cat.id} className="bg-white dark:bg-gray-800 rounded shadow p-4 flex flex-col">
            <div className="flex-1">
              <h2 className="font-semibold text-lg mb-2">{cat.name || 'Unnamed Category'}</h2>
              <p className="text-sm text-gray-500">{cat.description || 'No description provided'}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
