import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/layout/Layout';
import Login from '@/pages/Login';
import Signup from '@/pages/Signup';
import Home from '@/pages/Home';
import Properties from '@/pages/Properties';
import PropertyDetail from '@/pages/PropertyDetail';
import Dashboard from '@/pages/Dashboard';
import CreateProperty from '@/pages/CreateProperty';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/properties" element={<Properties />} />
            <Route path="/properties/:id" element={<PropertyDetail />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/create-property" element={<CreateProperty />} />
          </Route>
        </Routes>
      </div>
    </AuthProvider>
  );
}

export default App;
