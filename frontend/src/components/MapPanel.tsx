import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

// Default Leaflet marker icons reference bundler-hashed asset paths that
// break under Vite; point them at the CDN copies instead.
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapPanelProps {
  latitude: number;
  longitude: number;
  label?: string;
}

export default function MapPanel({ latitude, longitude, label }: MapPanelProps) {
  return (
    <div className="h-56 w-full overflow-hidden rounded-lg border border-slate-200">
      <MapContainer
        center={[latitude, longitude]}
        zoom={9}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[latitude, longitude]} icon={icon}>
          <Popup>{label || `${latitude.toFixed(3)}, ${longitude.toFixed(3)}`}</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
