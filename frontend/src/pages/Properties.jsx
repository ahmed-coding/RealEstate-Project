import React, { useEffect, useState } from 'react';
import { getProperties } from '@/api/properties';
import { getCategories, getStates } from '@/api/core';
import PropertyCard from '@/components/properties/PropertyCard';
import { Input } from '@/components/common/Input';
import { Loader2, Search, Filter } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export default function Properties() {
    const [properties, setProperties] = useState([]);
    const [categories, setCategories] = useState([]);
    const [states, setStates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchParams, setSearchParams] = useSearchParams();

    // Filters state
    const [filters, setFilters] = useState({
        search: searchParams.get('search') || '',
        category: searchParams.get('category') || '',
        state: searchParams.get('state') || '',
        min_price: '',
        max_price: '',
    });

    useEffect(() => {
        // Fetch initial filter data
        const fetchFilterData = async () => {
            try {
                const [cats, stts] = await Promise.all([
                    getCategories({ page_size: 100 }),
                    getStates({ page_size: 100 })
                ]);
                setCategories(cats.results || []);
                setStates(stts || []);
            } catch (e) {
                console.error("Failed to load filter options", e);
            }
        };
        fetchFilterData();
    }, []);

    useEffect(() => {
        const fetchProperties = async () => {
            setLoading(true);
            try {
                const params = {
                    search: filters.search,
                    category: filters.category,
                    // API might expect 'state' param? Schema said 'state' in description but verify.
                    // Using query params directly.
                    ...filters
                };
                // Clean empty filters
                Object.keys(params).forEach(key => (params[key] === '' || params[key] === null) && delete params[key]);

                const data = await getProperties(params);
                setProperties(data.results || []);
            } catch (error) {
                console.error("Failed to fetch properties", error);
            } finally {
                setLoading(false);
            }
        };

        fetchProperties();
    }, [filters]); // Re-fetch when filters change (debouncing would be better for search)

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({ ...prev, [name]: value }));
        // Update URL params
        if (value) {
            searchParams.set(name, value);
        } else {
            searchParams.delete(name);
        }
        setSearchParams(searchParams);
    };

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <h1 className="text-3xl font-bold text-gray-900">All Properties</h1>

                {/* Search Bar */}
                <div className="relative w-full md:w-96">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <Search className="h-5 w-5 text-gray-400" />
                    </div>
                    <Input
                        name="search"
                        placeholder="Search properties..."
                        className="pl-10"
                        value={filters.search}
                        onChange={handleFilterChange}
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Sidebar Filters */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
                        <div className="flex items-center gap-2 font-semibold text-lg mb-4 text-gray-900">
                            <Filter className="h-5 w-5" />
                            Filters
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                <select
                                    name="category"
                                    value={filters.category}
                                    onChange={handleFilterChange}
                                    className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                >
                                    <option value="">All Categories</option>
                                    {categories.map(c => (
                                        <option key={c.id} value={c.id}>{c.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                                <select
                                    name="state"
                                    value={filters.state}
                                    onChange={handleFilterChange}
                                    className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                >
                                    <option value="">All States</option>
                                    {states.map(s => (
                                        <option key={s.id} value={s.id}>{s.name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Price Range */}
                            {/* Can be added if API supports min/max price query params directly */}
                        </div>
                    </div>
                </div>

                {/* Properties Grid */}
                <div className="lg:col-span-3">
                    {loading ? (
                        <div className="flex justify-center py-20">
                            <Loader2 className="h-10 w-10 animate-spin text-primary-500" />
                        </div>
                    ) : properties.length === 0 ? (
                        <div className="text-center py-20 bg-white rounded-lg border border-dashed border-gray-300">
                            <p className="text-gray-500 text-lg">No properties found matching your criteria.</p>
                            <button onClick={() => setFilters({ search: '', category: '', state: '', min_price: '', max_price: '' })} className="mt-2 text-primary-600 hover:underline">
                                Clear all filters
                            </button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {properties.map(property => (
                                <PropertyCard key={property.id} property={property} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
