import React from 'react';
import Navbar from './Navbar';
import { Outlet } from 'react-router-dom';

export default function Layout() {
    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <main>
                <Outlet />
            </main>
            <footer className="bg-white border-t mt-12">
                <div className="mx-auto max-w-7xl px-6 py-8 md:flex md:items-center md:justify-between lg:px-8">
                    <p className="text-center text-xs leading-5 text-gray-500">&copy; 2024 RealEstate Inc. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
