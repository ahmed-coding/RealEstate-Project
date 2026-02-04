import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchProperty, deleteProperty } from '../api/property';

function PropertyDetail() {
  const { id } = useParams();
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProperty(id)
      .then(setProperty)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-pulse">Loading property...</div>;
  if (error) return <div className="text-red-500">Error loading property.</div>;
  if (!property) return <div>Property not found.</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded shadow p-6">
      <h1 className="text-2xl font-bold mb-2">{property.title || 'Untitled Property'}</h1>
      <p className="mb-2">{property.address || 'No address provided'}</p>
      <div className="flex gap-2 mt-4">
        <Link to={`/property/${id}/edit`} className="px-3 py-2 rounded bg-[var(--color-secondary)] text-white">Edit</Link>
        <button onClick={() => deleteProperty(id).then(() => navigate('/'))} className="px-3 py-2 rounded bg-red-500 text-white">Delete</button>
      </div>
    </div>
  );
}

export default PropertyDetail;
