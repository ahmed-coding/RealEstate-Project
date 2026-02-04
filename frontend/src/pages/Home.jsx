import React, { useEffect, useState } from 'react';
import { getBanners, getCategories } from '@/api/core';
import { getProperties } from '@/api/properties'; // Maybe fetch featured properties
import { Link } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/common/Button';

export default function Home() {
    const [banners, setBanners] = useState([]);
    const [categories, setCategories] = useState([]);
    const [featuredProperties, setFeaturedProperties] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [bannersData, categoriesData, propertiesData] = await Promise.all([
                    getBanners(),
                    getCategories({ page_size: 6 }), // Top 6 categories
                    getProperties({ is_featured: true, page_size: 3 })
                ]);
                setBanners(Array.isArray(bannersData) ? bannersData : []);
                setCategories(categoriesData.results || []); // Pagination result
                setFeaturedProperties(propertiesData.results || []);
            } catch (error) {
                console.error("Failed to fetch home data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary-500" /></div>;
    }

    return (
        <div className="space-y-16 pb-16">
            {/* Hero / Banners Section */}
            <section className="relative bg-gray-900 text-white">
                {/* Simplified Hero if no banners, else Carousel */}
                {banners.length > 0 ? (
                    <div className="relative h-[500px] w-full overflow-hidden">
                        {/* Just showing the first banner for simplicity in MVP */}
                        <img src={banners[0].image} alt="Banner" className="h-full w-full object-cover opacity-50" />
                        <div className="absolute inset-0 flex items-center justify-center p-4">
                            <div className="text-center">
                                <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl">{banners[0].title || "Find Your Dream Home"}</h1>
                                <p className="mt-6 max-w-lg mx-auto text-xl">{banners[0].description || "Thousands of properties are waiting for you."}</p>
                                <div className="mt-10 flex justify-center gap-4">
                                    <Link to="/properties">
                                        <Button size="lg" className="bg-white text-gray-900 hover:bg-gray-100">Browse Properties</Button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="py-24 px-6 text-center">
                        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl">Find Your Dream Home</h1>
                        <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-300">Discover the perfect property from our extensive list of real estate.</p>
                        <div className="mt-10">
                            <Link to="/properties">
                                <Button size="lg">Browse Properties</Button>
                            </Link>
                        </div>
                    </div>
                )}
            </section>

            {/* Categories Section */}
            <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <h2 className="text-3xl font-bold tracking-tight text-gray-900">Explore by Category</h2>
                <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {categories.map((category) => (
                        <div key={category.id} className="group relative overflow-hidden rounded-lg bg-white shadow-md transition-shadow hover:shadow-lg border border-gray-100">
                            <div className="aspect-h-1 aspect-w-1 w-full overflow-hidden bg-gray-200 lg:aspect-none group-hover:opacity-75 lg:h-48">
                                {category.image ? (
                                    <img src={category.image} alt={category.name} className="h-full w-full object-cover object-center lg:h-full lg:w-full" />
                                ) : (
                                    <div className="flex h-full items-center justify-center bg-gray-100 text-gray-400">No Image</div>
                                )}
                            </div>
                            <div className="p-4">
                                <h3 className="text-lg font-medium text-gray-900">
                                    <Link to={`/properties?category=${category.id}`}>
                                        <span aria-hidden="true" className="absolute inset-0" />
                                        {category.name}
                                    </Link>
                                </h3>
                                <p className="mt-1 text-sm text-gray-500">{category.count || '0'} Properties</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Featured Properties Section */}
            <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between">
                    <h2 className="text-3xl font-bold tracking-tight text-gray-900">Featured Properties</h2>
                    <Link to="/properties?is_featured=true" className="text-sm font-medium text-primary-600 hover:text-primary-500">
                        View all
                    </Link>
                </div>
                <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {featuredProperties.map((property) => (
                        <div key={property.id} className="group relative overflow-hidden rounded-lg bg-white shadow-md border border-gray-100">
                            <div className="aspect-h-1 aspect-w-1 w-full overflow-hidden bg-gray-200 lg:aspect-none lg:h-64">
                                {/* Assuming property.image is array or first image */}
                                {property.image && property.image.length > 0 ? (
                                    <img src={property.image[0].image} alt={property.name} className="h-full w-full object-cover object-center lg:h-full lg:w-full" />
                                ) : (
                                    <div className="flex h-full items-center justify-center bg-gray-100 text-gray-400">No Image</div>
                                )}
                            </div>
                            <div className="p-4">
                                <h3 className="text-lg font-semibold text-gray-900">
                                    <Link to={`/property/${property.id}`}>
                                        <span aria-hidden="true" className="absolute inset-0" />
                                        {property.name}
                                    </Link>
                                </h3>
                                <p className="mt-1 text-primary-600 font-bold">${property.price}</p>
                                <p className="mt-2 text-sm text-gray-500 line-clamp-2">{property.description}</p>
                                <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
                                    {property.size && <span>{property.size} sqft</span>}
                                    {/* Address would be nice here if available in list view */}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
