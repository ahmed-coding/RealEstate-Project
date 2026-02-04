import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchProperty, updateProperty } from '../api/property';

function PropertyEdit() {
  const { id } = useParams();
  const [form, setForm] = useState({ title: '', address: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProperty(id)
      .then((data) => setForm({ title: data.title || '', address: data.address || '' }))
      .catch(() => setError('Failed to load property'))
      .finally(() => setLoading(false));
  }, [id]);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await updateProperty(id, form);
      navigate(`/property/${id}`);
    } catch (err) {
      setError('Failed to update property');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="animate-pulse">Loading...</div>;

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded shadow p-6">
      <h1 className="text-xl font-bold mb-4">Edit Property</h1>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Title</label>
        <input name="title" value={form.title} onChange={handleChange} required className="w-full p-2 border rounded" />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Address</label>
        <input name="address" value={form.address} onChange={handleChange} required className="w-full p-2 border rounded" />
      </div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-[var(--color-primary)] text-white">
        {loading ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}

export default PropertyEdit;
