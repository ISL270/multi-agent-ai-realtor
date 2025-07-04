import React from 'react';

// --- Data Interface ---
export interface Property {
  id: string;
  title: string;
  price: number;
  bedrooms?: number;
  bathrooms?: number;
  area_sqm?: number;
  city?: string;
  image_url: string;
  amenities?: string[];
}

// --- SVG Icons ---
const BedIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 4v16h20V4H2z" /><path d="M2 12h20" /><path d="M7 12V4" /><path d="M17 12V4" /></svg>
);

const BathIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 6l2 2" /><path d="M13 6l-2 2" /><path d="M11 18H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h18a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-4" /><path d="M11 14v4" /></svg>
);

const AreaIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 3H3v18h18V3z" /><path d="M12 3v18" /><path d="M3 12h18" /></svg>
);

// --- Property Card Component ---
interface PropertyCardProps {
  property: Property;
}

export const PropertyCard: React.FC<PropertyCardProps> = ({ property }) => {
  const {
    title,
    price,
    bedrooms,
    bathrooms,
    area_sqm,
    city,
    image_url,
    amenities,
  } = property;

  return (
    <div className="group relative flex flex-col overflow-hidden rounded-lg shadow-lg transition-shadow duration-300 hover:shadow-xl bg-white">
      <div className="relative">
        <img
          src={image_url}
          alt={`Image of ${title}`}
          className="h-48 w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {city && (
          <div className="absolute top-3 right-3 rounded-full bg-white/80 px-3 py-1 text-sm font-medium text-gray-900 backdrop-blur-sm">
            {city}
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col p-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-2xl font-bold text-blue-600">${price.toLocaleString()}</p>
          <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
            {bedrooms && (
              <div className="flex items-center space-x-1">
                <BedIcon />
                <span>{bedrooms} Beds</span>
              </div>
            )}
            {bathrooms && (
              <div className="flex items-center space-x-1">
                <BathIcon />
                <span>{bathrooms} Baths</span>
              </div>
            )}
            {area_sqm && (
              <div className="flex items-center space-x-1">
                <AreaIcon />
                <span>{area_sqm} m²</span>
              </div>
            )}
          </div>
        </div>
        {amenities && amenities.length > 0 && (
          <div className="mt-4 border-t pt-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Amenities</h4>
            <div className="flex flex-wrap gap-2 mt-2">
              {amenities.map((amenity) => (
                <span
                  key={amenity}
                  className="px-2 py-1 bg-gray-200 text-gray-800 text-xs font-medium rounded-full"
                >
                  {amenity}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Property List Component ---
export interface PropertyListProps {
  properties: Property[];
}

export const PropertyList: React.FC<PropertyListProps> = ({ properties }) => {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 p-4">
      {properties.map((property) => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
};

// --- Component Mapping for LangGraph ---
export default {
  PropertyList,
};