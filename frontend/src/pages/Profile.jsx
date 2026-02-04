import React, { useEffect, useState } from 'react';
import client from '../api/client';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    client.get('user/profile/')
      .then(r => setProfile(r.data))
      .catch(() => setError('Failed to load profile'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse">Loading profile...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!profile) return <div>No profile found.</div>;

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <div className="mb-2"><strong>Name:</strong> {profile.name || 'N/A'}</div>
      <div className="mb-2"><strong>Email:</strong> {profile.email || 'N/A'}</div>
      {/* Add more profile fields as needed */}
    </div>
  );
}
