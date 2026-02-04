import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProperty } from '../api/property';

function PropertyCreate() {
  const [form, setForm] = useState({ title: '', address: '' });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createProperty(form);
      navigate('/');
    } catch (err) {
      setError('Failed to create property');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded shadow p-6">
      <h1 className="text-xl font-bold mb-4">Add Property</h1>
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
        {loading ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
}

export default PropertyCreate;
