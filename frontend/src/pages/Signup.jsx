import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Loader2 } from 'lucide-react';

export default function Signup() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        name: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            // The schema requires 'user_auth' object, but usually serializer handles nested defaults?
            // Wait, UserAuth schema says `user_auth` is READ ONLY.
            // And `password` is writeOnly.
            // So we just send fields.
            await signup({
                ...formData,
                // user_type: 'customer' // Optional
            });
            // After signup, redirect to login or home? 
            // Often better to login immediately, but let's go to login for safety.
            navigate('/login');
        } catch (err) {
            console.error(err);
            setError('Signup failed. Please check your data.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
            <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-lg">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
                        Create an account
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Already have an account?{' '}
                        <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                            Sign in
                        </Link>
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700">Full Name</label>
                            <Input
                                id="name"
                                name="name"
                                type="text"
                                required
                                className="mt-1"
                                placeholder="John Doe"
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
                            <Input
                                id="username"
                                name="username"
                                type="text"
                                required
                                className="mt-1"
                                placeholder="username"
                                value={formData.username}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                            <Input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="mt-1"
                                placeholder="name@example.com"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="user_type" className="block text-sm font-medium text-gray-700">Account Type</label>
                            <select
                                id="user_type"
                                name="user_type"
                                className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                value={formData.user_type || 'customer'}
                                onChange={handleChange}
                            >
                                <option value="customer">Customer (I want to buy/rent)</option>
                                <option value="owner">Owner (I want to sell/rent out)</option>
                                <option value="agent">Agent</option>
                            </select>
                        </div>
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="mt-1"
                                placeholder="Password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-sm text-red-500 text-center">{error}</div>
                    )}

                    <div>
                        <Button
                            type="submit"
                            className="w-full"
                            disabled={loading}
                        >
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Create Account'}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
