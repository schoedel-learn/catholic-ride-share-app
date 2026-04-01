"use client";

import React, { useMemo } from "react";
import { GoogleMap, useLoadScript, Marker, DirectionsRenderer } from "@react-google-maps/api";

type Location = { latitude: number; longitude: number };

interface RideMapProps {
  pickup: Location;
  dropoff: Location;
}

const mapContainerStyle = {
  width: "100%",
  height: "100%",
};

export default function RideMap({ pickup, dropoff }: RideMapProps) {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "",
  });

  const [directions, setDirections] = React.useState<google.maps.DirectionsResult | null>(null);

  // Center map approximately between pickup and dropoff
  const center = useMemo(() => {
    return {
      lat: (pickup.latitude + dropoff.latitude) / 2,
      lng: (pickup.longitude + dropoff.longitude) / 2,
    };
  }, [pickup, dropoff]);

  React.useEffect(() => {
    if (!isLoaded) return;

    try {
      const directionsService = new window.google.maps.DirectionsService();
      directionsService.route(
        {
          origin: { lat: pickup.latitude, lng: pickup.longitude },
          destination: { lat: dropoff.latitude, lng: dropoff.longitude },
          travelMode: window.google.maps.TravelMode.DRIVING,
        },
        (result, status) => {
          if (status === window.google.maps.DirectionsStatus.OK && result) {
            setDirections(result);
          } else {
            console.error(`error fetching directions ${result}`);
          }
        }
      );
    } catch (e) {
      console.error("Setup directions error", e);
    }
  }, [isLoaded, pickup, dropoff]);

  if (loadError) return <div className="text-red-400 text-xs">Error loading maps</div>;
  if (!isLoaded) return <div className="text-slate-400 text-xs flex items-center justify-center p-4">Loading maps...</div>;

  return (
    <div className="w-full h-full min-h-[250px] rounded-md overflow-hidden bg-slate-800">
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        zoom={12}
        center={center}
        options={{
          disableDefaultUI: true,
          zoomControl: true,
          styles: [
            { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
            { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
            {
              featureType: "administrative.locality",
              elementType: "labels.text.fill",
              stylers: [{ color: "#d59563" }],
            },
            {
              featureType: "poi",
              elementType: "labels.text.fill",
              stylers: [{ color: "#d59563" }],
            },
            {
              featureType: "poi.park",
              elementType: "geometry",
              stylers: [{ color: "#263c3f" }],
            },
            {
              featureType: "poi.park",
              elementType: "labels.text.fill",
              stylers: [{ color: "#6b9a76" }],
            },
            {
              featureType: "road",
              elementType: "geometry",
              stylers: [{ color: "#38414e" }],
            },
            {
              featureType: "road",
              elementType: "geometry.stroke",
              stylers: [{ color: "#212a37" }],
            },
            {
              featureType: "road",
              elementType: "labels.text.fill",
              stylers: [{ color: "#9ca5b3" }],
            },
            {
              featureType: "road.highway",
              elementType: "geometry",
              stylers: [{ color: "#746855" }],
            },
            {
              featureType: "road.highway",
              elementType: "geometry.stroke",
              stylers: [{ color: "#1f2835" }],
            },
            {
              featureType: "road.highway",
              elementType: "labels.text.fill",
              stylers: [{ color: "#f3d19c" }],
            },
            {
              featureType: "transit",
              elementType: "geometry",
              stylers: [{ color: "#2f3948" }],
            },
            {
              featureType: "transit.station",
              elementType: "labels.text.fill",
              stylers: [{ color: "#d59563" }],
            },
            {
              featureType: "water",
              elementType: "geometry",
              stylers: [{ color: "#17263c" }],
            },
            {
              featureType: "water",
              elementType: "labels.text.fill",
              stylers: [{ color: "#515c6d" }],
            },
            {
              featureType: "water",
              elementType: "labels.text.stroke",
              stylers: [{ color: "#17263c" }],
            },
          ],
        }}
      >
        {directions ? (
          <DirectionsRenderer
            directions={directions}
            options={{
              polylineOptions: {
                strokeColor: "#10b981", // emerald-500
                strokeWeight: 4,
                strokeOpacity: 0.8,
              },
              suppressMarkers: false,
            }}
          />
        ) : (
          <>
            <Marker position={{ lat: pickup.latitude, lng: pickup.longitude }} label="A" />
            <Marker position={{ lat: dropoff.latitude, lng: dropoff.longitude }} label="B" />
          </>
        )}
      </GoogleMap>
    </div>
  );
}
