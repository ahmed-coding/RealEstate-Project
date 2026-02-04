import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getProperties } from '../api/property';

export default function PropertyList() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getProperties()
      .then(setProperties)
      .catch(() => setError('Failed to load properties'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse">Loading properties...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!properties.length) return <div>No properties found.</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Properties</h1>
      <ul className="grid gap-4 md:grid-cols-2">
        {properties.map((prop) => (
          <li key={prop.id} className="bg-white dark:bg-gray-800 rounded shadow p-4 flex flex-col">
            <div className="flex-1">
              <h2 className="font-semibold text-lg mb-2">{prop.title || 'Untitled Property'}</h2>
              <p className="text-sm text-gray-500">{prop.address || 'No address provided'}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <Link to={`/property/${prop.id}`} className="text-[var(--color-primary)] underline">View</Link>
              <Link to={`/property/${prop.id}/edit`} className="text-[var(--color-secondary)] underline">Edit</Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
