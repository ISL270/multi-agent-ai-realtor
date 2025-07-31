import React from 'react';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./carousel";
import './output.css';

interface Property {
  id: string;
  title: string;
  description: string | null;
  price: number;
  property_type: string | null;
  bedrooms: number | null;
  bathrooms: number | null;
  area_sqm: number | null;
  city: string | null;
  image_url: string;
  amenities: string[];
}

// A detailed card that displays all property information, as requested.
const PropertyCard = ({ property }: { property: Property }) => {
  return (
    <div
      className="relative w-[161px] h-[256px] rounded-2xl shadow-md overflow-hidden"
      style={{
        backgroundImage: `url(${property.image_url})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute bottom-0 left-0 right-0 flex flex-col gap-1 p-3 text-white bg-gradient-to-t from-black/70 to-transparent">
        <p className="text-sm font-semibold">{property.title}</p>
        <div className="flex items-center gap-1 text-xs">
          <p>${property.price.toLocaleString()}</p>
        </div>
        <p className="text-sm">{property.city}</p>
      </div>
    </div>
  );
};

// Main component to be called from the agent.
// Renders a non-interactive carousel of detailed property cards.
const PropertyCarousel = ({ properties }: { properties: Property[] }) => {
  if (!properties || properties.length === 0) {
    return null; // Don't render anything if there are no properties
  }

  return (
    <div className="space-y-8">
      <Carousel
        opts={{
          align: "start",
          loop: true,
        }}
        className="w-full sm:max-w-sm md:max-w-3xl lg:max-w-3xl"
      >
        <CarouselContent>
          {properties.map((property) => (
            <CarouselItem key={property.id} className="sm:basis-1/2 md:basis-1/3 lg:basis-1/4 p-2">
              <PropertyCard property={property} />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
};

// --- COMPONENT MAP ---
// This is the mapping from string names (used in the backend) to React components.
export default {
  property_carousel: PropertyCarousel,
};