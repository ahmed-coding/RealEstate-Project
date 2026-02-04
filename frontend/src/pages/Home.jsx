import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="flex flex-col gap-8 items-center justify-center py-12">
      <h1 className="text-3xl font-bold text-[var(--color-primary)]">Welcome to RealEstate</h1>
      <p className="max-w-xl text-center text-lg text-[var(--color-secondary)]">Find, review, and favorite properties. Explore categories, banners, and more. All user-facing, mobile-first, and theme-ready.</p>
      <div className="flex gap-4 flex-wrap justify-center">
        <Link to="/properties" className="px-4 py-2 rounded bg-[var(--color-primary)] text-white">Browse Properties</Link>
        <Link to="/favorites" className="px-4 py-2 rounded bg-[var(--color-secondary)] text-white">My Favorites</Link>
        <Link to="/profile" className="px-4 py-2 rounded bg-[var(--color-accent)] text-white">Profile</Link>
      </div>
    </div>
  );
}
