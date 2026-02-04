import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProperty, getPropertyReviews, predictPrice } from '@/api/properties';
import { Loader2, MapPin, Check, Star, DollarSign } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { useAuth } from '@/context/AuthContext';

export default function PropertyDetail() {
    const { id } = useParams();
    const [property, setProperty] = useState(null);
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeImage, setActiveImage] = useState(0);

    // Prediction State
    const [prediction, setPrediction] = useState(null);
    const [predictLoading, setPredictLoading] = useState(false);
    const { user } = useAuth(); // Maybe check if user is allowed to predict?

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [propData, reviewsData] = await Promise.all([
                    getProperty(id),
                    getPropertyReviews(id) // Optional: wrap in try/catch if it fails independent of property
                ]);
                setProperty(propData);
                setReviews(reviewsData.results || []);
            } catch (error) {
                console.error("Error loading property:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const handlePredictPrice = async () => {
        setPredictLoading(true);
        try {
            // The API expects 'query' integer? Schema says: query: integer
            // Description: `query`: query to get Predicting Price For Property in `POST Method`
            // It seems we just send the property ID as 'query'?
            // Let's try sending { query: id }
            const res = await predictPrice({ query: parseInt(id) });
            setPrediction(res.price);
        } catch (error) {
            console.error("Prediction failed", error);
            alert("Could not predict price at this time.");
        } finally {
            setPredictLoading(false);
        }
    };

    if (loading) return <div className="flex h-screen items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary-500" /></div>;
    if (!property) return <div className="p-8 text-center">Property not found.</div>;

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900">{property.name}</h1>
                <div className="flex items-center text-gray-500 mt-2">
                    <MapPin className="h-4 w-4 mr-1" />
                    <span>
                        {property.address?.line1}, {property.address?.city_name}, {property.address?.state_name}, {property.address?.country_name}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Image Gallery */}
                    <div className="space-y-4">
                        <div className="aspect-w-16 aspect-h-9 w-full overflow-hidden rounded-lg bg-gray-200">
                            {property.image && property.image.length > 0 ? (
                                <img
                                    src={property.image[activeImage].image}
                                    alt={property.name}
                                    className="h-full w-full object-cover object-center"
                                />
                            ) : (
                                <div className="flex items-center justify-center h-96 text-gray-400">No Images</div>
                            )}
                        </div>
                        {property.image && property.image.length > 1 && (
                            <div className="flex gap-4 overflow-x-auto pb-2">
                                {property.image.map((img, idx) => (
                                    <button
                                        key={img.id}
                                        onClick={() => setActiveImage(idx)}
                                        className={`flex-shrink-0 w-24 h-24 rounded-md overflow-hidden border-2 ${activeImage === idx ? 'border-primary-500' : 'border-transparent'}`}
                                    >
                                        <img src={img.image} alt="" className="h-full w-full object-cover" />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Description */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4">Description</h2>
                        <p className="text-gray-700 whitespace-pre-line">{property.description}</p>
                    </div>

                    {/* Features */}
                    {property.feature_property && property.feature_property.length > 0 && (
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                            <h2 className="text-xl font-semibold mb-4">Features</h2>
                            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {property.feature_property.map((fp) => (
                                    <li key={fp.id} className="flex items-center text-gray-700">
                                        <Check className="h-5 w-5 text-green-500 mr-2" />
                                        {fp.feature?.name}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Details & Attributes */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4">Property Details</h2>
                        <div className="grid grid-cols-2 gap-y-4 text-sm">
                            <div className="text-gray-500">Price</div>
                            <div className="font-semibold text-lg">${property.price}</div>

                            <div className="text-gray-500">Size</div>
                            <div className="font-semibold">{property.size} m²</div>

                            <div className="text-gray-500">Type</div>
                            <div className="font-semibold capitalize">
                                {property.for_sale ? 'For Sale' : ''}
                                {property.for_sale && property.for_rent ? ' / ' : ''}
                                {property.for_rent ? 'For Rent' : ''}
                            </div>

                            {property.property_value && property.property_value.map(pv => (
                                <React.Fragment key={pv.id}>
                                    <div className="text-gray-500">{pv.value?.attribute?.name}</div>
                                    <div className="font-semibold">{pv.value?.value}</div>
                                </React.Fragment>
                            ))}
                        </div>
                    </div>

                    {/* Reviews */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4 flex items-center">
                            Reviews
                            <span className="ml-2 text-base font-normal text-gray-500">({reviews.length})</span>
                        </h2>
                        <div className="space-y-6">
                            {reviews.length === 0 ? (
                                <p className="text-gray-500">No reviews yet.</p>
                            ) : (
                                reviews.map(review => (
                                    <div key={review.id} className="border-b pb-4 last:border-0 last:pb-0">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-medium">User {review.user}</span>
                                            <div className="flex items-center text-yellow-400">
                                                <Star className="h-4 w-4 fill-current" />
                                                <span className="ml-1 text-gray-700">{review.rate_review}</span>
                                            </div>
                                        </div>
                                        <p className="text-gray-600">{review.review}</p>
                                        <p className="text-xs text-gray-400 mt-2">{new Date(review.time_created).toLocaleDateString()}</p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="lg:col-span-1 space-y-6">
                    {/* Contact / Price */}
                    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 sticky top-24">
                        <div className="text-3xl font-bold text-primary-600 mb-2">${property.price}</div>
                        <p className="text-gray-500 mb-6 flex items-center">
                            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${property.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                            {property.is_active ? 'Active Listing' : 'Inactive'}
                        </p>

                        <Button className="w-full mb-4" size="lg">Contact Agent</Button>

                        <div className="border-t pt-4 mt-4">
                            <h3 className="font-semibold mb-2">Price Prediction</h3>
                            <p className="text-sm text-gray-500 mb-4">
                                Get an AI-estimated price for this property based on market trends.
                            </p>

                            {prediction ? (
                                <div className="bg-primary-50 p-4 rounded-md text-center mb-4">
                                    <div className="text-sm text-primary-600 font-medium">Estimated Price</div>
                                    <div className="text-2xl font-bold text-primary-700">${parseFloat(prediction).toLocaleString()}</div>
                                </div>
                            ) : (
                                <Button
                                    variant="outline"
                                    className="w-full"
                                    onClick={handlePredictPrice}
                                    disabled={predictLoading}
                                >
                                    {predictLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <DollarSign className="mr-2 h-4 w-4" />}
                                    Predict Price
                                </Button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
