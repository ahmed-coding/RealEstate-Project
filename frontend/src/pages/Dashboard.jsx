import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getProperties } from '@/api/properties';
import PropertyCard from '@/components/properties/PropertyCard';
import { Loader2, Plus } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Link } from 'react-router-dom';

export default function Dashboard() {
    const { user } = useAuth();
    const [myProperties, setMyProperties] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMyProperties = async () => {
            if (!user?.id) {
                setLoading(false);
                return;
            }
            try {
                const data = await getProperties({ user: user.id });
                setMyProperties(data.results || []);
            } catch (error) {
                console.error("Failed to fetch my properties", error);
            } finally {
                setLoading(false);
            }
        };
        fetchMyProperties();
    }, [user]);

    if (!user) {
        return <div className="p-8 text-center">Please log in to view your dashboard.</div>;
    }

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-white shadow rounded-lg p-6 mb-8">
                <div className="flex items-center gap-4">
                    <div className="h-16 w-16 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-2xl font-bold">
                        {user.name ? user.name.charAt(0).toUpperCase() : user.username?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{user.name || user.username}</h1>
                        <p className="text-gray-500">{user.email}</p>
                    </div>
                </div>
            </div>

            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">My Properties</h2>
                <Link to="/create-property">
                    <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        List New Property
                    </Button>
                </Link>
            </div>

            {loading ? (
                <div className="flex justify-center py-10">
                    <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
                </div>
            ) : myProperties.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <p className="text-gray-500 mb-4">You haven't listed any properties yet.</p>
                    <Button variant="outline">Create your first listing</Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {myProperties.map(property => (
                        <PropertyCard key={property.id} property={property} />
                    ))}
                </div>
            )}
        </div>
    );
}
