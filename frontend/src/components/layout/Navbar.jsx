import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/common/Button';
import { Menu, X, Home, User, LogOut } from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-white shadow-sm sticky top-0 z-50">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 justify-between">
                    <div className="flex">
                        <Link to="/" className="flex flex-shrink-0 items-center">
                            <Home className="h-6 w-6 text-primary-600 mr-2" />
                            <span className="font-bold text-xl text-gray-900">RealEstate</span>
                        </Link>
                        <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <Link to="/" className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700">
                                Home
                            </Link>
                            <Link to="/properties" className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700">
                                Properties
                            </Link>
                        </div>
                    </div>
                    <div className="hidden sm:ml-6 sm:flex sm:items-center space-x-4">
                        {user ? (
                            <>
                                <span className="text-sm text-gray-700">Hello, {user.name || user.username}</span>
                                <Link to="/dashboard">
                                    <Button variant="outline" size="sm" className="mr-2">Dashboard</Button>
                                </Link>
                                <Button variant="ghost" size="sm" onClick={handleLogout}>
                                    <LogOut className="h-4 w-4 mr-2" />
                                    Logout
                                </Button>
                            </>
                        ) : (
                            <div className="space-x-2">
                                <Link to="/login">
                                    <Button variant="ghost" size="sm">Log in</Button>
                                </Link>
                                <Link to="/signup">
                                    <Button size="sm">Sign up</Button>
                                </Link>
                            </div>
                        )}
                    </div>
                    <div className="-mr-2 flex items-center sm:hidden">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                        >
                            <span className="sr-only">Open main menu</span>
                            {isOpen ? <X className="block h-6 w-6" /> : <Menu className="block h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {isOpen && (
                <div className="sm:hidden">
                    <div className="space-y-1 pb-3 pt-2">
                        <Link to="/" className="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700">Home</Link>
                        <Link to="/properties" className="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700">Properties</Link>
                    </div>
                    <div className="border-t border-gray-200 pb-3 pt-4">
                        {user ? (
                            <div className="space-y-1">
                                <div className="px-4 text-sm text-gray-700">
                                    Hello, {user.name || user.username}
                                </div>
                                <button onClick={handleLogout} className="block w-full text-left border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700">
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-1">
                                <Link to="/login" className="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700">Log in</Link>
                                <Link to="/signup" className="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700">Sign up</Link>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
}
