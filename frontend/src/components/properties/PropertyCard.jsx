import React from 'react';
import { Link } from 'react-router-dom';

export default function PropertyCard({ property }) {
    return (
        <div className="group relative overflow-hidden rounded-lg bg-white shadow-md border border-gray-100 transition-all hover:shadow-lg">
            <div className="aspect-h-1 aspect-w-1 w-full overflow-hidden bg-gray-200 lg:aspect-none lg:h-64">
                {property.image && property.image.length > 0 ? (
                    <img
                        src={property.image[0].image}
                        alt={property.name}
                        className="h-full w-full object-cover object-center lg:h-full lg:w-full group-hover:scale-105 transition-transform duration-300"
                    />
                ) : (
                    <div className="flex h-full items-center justify-center bg-gray-100 text-gray-400">
                        No Image
                    </div>
                )}
                <div className="absolute top-2 right-2 flex flex-col gap-2">
                    {property.for_sale && <span className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">For Sale</span>}
                    {property.for_rent && <span className="bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded">For Rent</span>}
                </div>
            </div>
            <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600">
                    <Link to={`/properties/${property.id}`}>
                        <span aria-hidden="true" className="absolute inset-0" />
                        {property.name}
                    </Link>
                </h3>
                <p className="mt-1 text-primary-600 font-bold text-lg">${property.price}</p>
                <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                    {property.description}
                </p>
                <div className="mt-4 flex items-center justify-between text-xs text-gray-500 border-t pt-2">
                    <div className="flex gap-4">
                        {property.size && <span>{property.size} m²</span>}
                        {/* Add beds/baths if available in schema later, currently size is main attr */}
                    </div>
                    {property.address && property.address.state_name && <span>{property.address.state_name}</span>}
                </div>
            </div>
        </div>
    );
}
