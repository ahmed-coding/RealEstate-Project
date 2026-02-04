import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getCategories, getStates } from '@/api/core';
import { getProperty } from '@/api/properties'; // You'll need to export an updateProperty function from api/properties
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Loader2 } from 'lucide-react';
import client from '@/api/client';

export default function EditProperty() {
    const { id } = useParams();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [states, setStates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        size: '',
        category: '',
        for_sale: true,
        for_rent: false,
        state: '',
        line1: '',
        is_active: true
    });

    useEffect(() => {
        async function fetchData() {
            try {
                const [cats, stts, prop] = await Promise.all([
                    getCategories({ page_size: 100 }),
                    getStates({ page_size: 100 }),
                    getProperty(id)
                ]);
                setCategories(cats.results || []);
                setStates(stts || []);

                // Populate form
                setFormData({
                    name: prop.name || '',
                    description: prop.description || '',
                    price: prop.price || '',
                    size: prop.size || '',
                    category: prop.category?.id || prop.category || '', // Depends on if getProperty returns ID or object. Validated to return object in Detail view.
                    for_sale: prop.for_sale,
                    for_rent: prop.for_rent,
                    state: prop.address?.state?.id || prop.address?.state || '',
                    line1: prop.address?.line1 || '',
                    is_active: prop.is_active
                });
            } catch (error) {
                console.error("Failed to fetch data", error);
                // Handle error (e.g. not found or unauthorized)
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [id]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);

        try {
            const payload = {
                name: formData.name,
                description: formData.description,
                price: formData.price,
                size: parseInt(formData.size),
                category: parseInt(formData.category),
                for_sale: formData.for_sale,
                for_rent: formData.for_rent,
                is_active: formData.is_active,
                // API might handle address update differently (nested or separate). 
                // Schema implies address fields can be in property payload for creation, 
                // but for update it might be strict.
                // Let's assume PUT/PATCH allows similar structure or we might need to update Address separately if backend is strict.
                // Using PATCH to property endpoint.
                address: {
                    state: parseInt(formData.state),
                    line1: formData.line1,
                    latitude: 0,
                    longitude: 0,
                },
                // Note: Schema for update might require IDs for nested update or partial data.
            };

            await client.patch(`/property/${id}/update/`, payload);
            navigate('/dashboard');
        } catch (error) {
            console.error("Failed to update property", error);
            alert("Failed to update property.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="mx-auto max-w-2xl px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Edit Property</h1>
            <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-sm border border-gray-100">

                <div>
                    <label className="block text-sm font-medium text-gray-700">Property Name</label>
                    <Input name="name" required value={formData.name} onChange={handleChange} />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                        name="description"
                        required
                        value={formData.description}
                        onChange={handleChange}
                        className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Price ($)</label>
                        <Input name="price" type="number" required value={formData.price} onChange={handleChange} />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Size (m²)</label>
                        <Input name="size" type="number" required value={formData.size} onChange={handleChange} />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Category</label>
                        <select name="category" required value={formData.category} onChange={handleChange} className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm">
                            <option value="">Select Category</option>
                            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">State</label>
                        <select name="state" required value={formData.state} onChange={handleChange} className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm">
                            <option value="">Select State</option>
                            {states.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Address Line</label>
                    <Input name="line1" required value={formData.line1} onChange={handleChange} />
                </div>

                <div className="flex gap-4">
                    <label className="flex items-center space-x-2">
                        <input type="checkbox" name="for_sale" checked={formData.for_sale} onChange={handleChange} className="rounded text-primary-600 focus:ring-primary-500" />
                        <span className="text-sm font-medium">For Sale</span>
                    </label>
                    <label className="flex items-center space-x-2">
                        <input type="checkbox" name="for_rent" checked={formData.for_rent} onChange={handleChange} className="rounded text-primary-600 focus:ring-primary-500" />
                        <span className="text-sm font-medium">For Rent</span>
                    </label>
                    <label className="flex items-center space-x-2">
                        <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange} className="rounded text-primary-600 focus:ring-primary-500" />
                        <span className="text-sm font-medium">Active Listing</span>
                    </label>
                </div>

                <div className="pt-4 flex gap-4">
                    <Button type="button" variant="outline" className="w-full" onClick={() => navigate('/dashboard')}>Cancel</Button>
                    <Button type="submit" className="w-full" disabled={saving}>
                        {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Save Changes'}
                    </Button>
                </div>
            </form>
        </div>
    );
}
