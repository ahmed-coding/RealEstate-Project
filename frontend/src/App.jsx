import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import PropertyList from './pages/PropertyList';
import Favorites from './pages/Favorites';
import Profile from './pages/Profile';
import PropertyDetail from './pages/PropertyDetail';
import PropertyCreate from './pages/PropertyCreate';
import PropertyEdit from './pages/PropertyEdit';
import CategoryList from './pages/CategoryList';

function App() {
  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
      <header className="shadow p-4 flex justify-between items-center">
        <Link to="/" className="font-bold text-lg text-[var(--color-primary)]">RealEstate</Link>
        <nav className="flex gap-4">
          <Link to="/properties" className="px-3 py-2 rounded bg-[var(--color-primary)] text-white">Browse Properties</Link>
          <Link to="/categories" className="px-3 py-2 rounded bg-[var(--color-secondary)] text-white">Categories</Link>
          <Link to="/favorites" className="px-3 py-2 rounded bg-[var(--color-secondary)] text-white">My Favorites</Link>
          <Link to="/profile" className="px-3 py-2 rounded bg-[var(--color-accent)] text-white">Profile</Link>
        </nav>
      </header>
      <main className="p-4 max-w-4xl mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/properties" element={<PropertyList />} />
          <Route path="/categories" element={<CategoryList />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/property/:id" element={<PropertyDetail />} />
          <Route path="/property/create" element={<PropertyCreate />} />
          <Route path="/property/:id/edit" element={<PropertyEdit />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
