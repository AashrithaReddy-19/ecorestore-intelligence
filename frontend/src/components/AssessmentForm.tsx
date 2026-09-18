import type { AssessmentInput } from "../types";

interface Props {
  value: AssessmentInput;
  onChange: (value: AssessmentInput) => void;
}

const ECOSYSTEM_TYPES = ["mangrove", "coastal", "wetland", "forest", "grassland", "cropland", "riparian", "dryland"];
const SALINITY = ["low", "moderate", "high"];
const RAINFALL = ["low", "irregular", "regular", "high"];
const TEMPERATURE = ["stable", "rising", "falling"];
const FRAGMENTATION = ["low", "moderate", "high"];

function field(label: string, htmlFor: string, children: React.ReactNode, hint?: string) {
  return (
    <label htmlFor={htmlFor} className="block text-sm">
      <span className="font-medium text-slate-700">{label}</span>
      {children}
      {hint && <span className="block text-xs text-slate-400 mt-0.5">{hint}</span>}
    </label>
  );
}

export default function AssessmentForm({ value, onChange }: Props) {
  const set = <K extends keyof AssessmentInput>(key: K, v: AssessmentInput[K]) =>
    onChange({ ...value, [key]: v });

  const inputClass =
    "mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-eco-500 focus:outline-none focus:ring-1 focus:ring-eco-500";

  return (
    <form className="grid grid-cols-1 md:grid-cols-2 gap-4" aria-label="Environmental assessment form">
      {field(
        "Location name",
        "location_name",
        <input
          id="location_name"
          className={inputClass}
          value={value.location_name ?? ""}
          onChange={(e) => set("location_name", e.target.value)}
        />
      )}

      <div className="grid grid-cols-2 gap-2">
        {field(
          "Latitude",
          "latitude",
          <input
            id="latitude"
            type="number"
            step="any"
            className={inputClass}
            value={value.latitude ?? ""}
            onChange={(e) => set("latitude", e.target.value === "" ? null : Number(e.target.value))}
          />
        )}
        {field(
          "Longitude",
          "longitude",
          <input
            id="longitude"
            type="number"
            step="any"
            className={inputClass}
            value={value.longitude ?? ""}
            onChange={(e) => set("longitude", e.target.value === "" ? null : Number(e.target.value))}
          />
        )}
      </div>

      {field(
        "Ecosystem type",
        "ecosystem_type",
        <select
          id="ecosystem_type"
          className={inputClass}
          value={value.ecosystem_type ?? ""}
          onChange={(e) => set("ecosystem_type", e.target.value)}
        >
          <option value="">Select...</option>
          {ECOSYSTEM_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      )}

      {field(
        "Land use",
        "land_use",
        <input
          id="land_use"
          className={inputClass}
          placeholder="e.g. degraded mangrove edge, monoculture cropland"
          value={value.land_use ?? ""}
          onChange={(e) => set("land_use", e.target.value)}
        />
      )}

      {field(
        "Soil organic carbon (%)",
        "soc",
        <input
          id="soc"
          type="number"
          step="any"
          min={0}
          max={100}
          className={inputClass}
          value={value.soil_organic_carbon_percent ?? ""}
          onChange={(e) =>
            set("soil_organic_carbon_percent", e.target.value === "" ? null : Number(e.target.value))
          }
        />
      )}

      {field(
        "Soil pH",
        "soil_ph",
        <input
          id="soil_ph"
          type="number"
          step="any"
          min={0}
          max={14}
          className={inputClass}
          value={value.soil_ph ?? ""}
          onChange={(e) => set("soil_ph", e.target.value === "" ? null : Number(e.target.value))}
        />
      )}

      {field(
        "Soil moisture (%)",
        "soil_moisture",
        <input
          id="soil_moisture"
          type="number"
          step="any"
          min={0}
          max={100}
          className={inputClass}
          value={value.soil_moisture_percent ?? ""}
          onChange={(e) =>
            set("soil_moisture_percent", e.target.value === "" ? null : Number(e.target.value))
          }
        />
      )}

      {field(
        "Soil salinity",
        "soil_salinity",
        <select
          id="soil_salinity"
          className={inputClass}
          value={value.soil_salinity ?? ""}
          onChange={(e) => set("soil_salinity", e.target.value)}
        >
          <option value="">Select...</option>
          {SALINITY.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      )}

      {field(
        "Rainfall pattern",
        "rainfall_pattern",
        <select
          id="rainfall_pattern"
          className={inputClass}
          value={value.rainfall_pattern ?? ""}
          onChange={(e) => set("rainfall_pattern", e.target.value)}
        >
          <option value="">Select...</option>
          {RAINFALL.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      )}

      {field(
        "Temperature trend",
        "temperature_trend",
        <select
          id="temperature_trend"
          className={inputClass}
          value={value.temperature_trend ?? ""}
          onChange={(e) => set("temperature_trend", e.target.value)}
        >
          <option value="">Select...</option>
          {TEMPERATURE.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      )}

      {field(
        "Habitat fragmentation",
        "habitat_fragmentation",
        <select
          id="habitat_fragmentation"
          className={inputClass}
          value={value.habitat_fragmentation ?? ""}
          onChange={(e) => set("habitat_fragmentation", e.target.value)}
        >
          <option value="">Select...</option>
          {FRAGMENTATION.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      )}

      {field(
        "Human impact (comma-separated)",
        "human_impact",
        <input
          id="human_impact"
          className={inputClass}
          placeholder="aquaculture expansion, plastic pollution"
          value={value.human_impact.join(", ")}
          onChange={(e) =>
            set(
              "human_impact",
              e.target.value
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean)
            )
          }
        />,
        "e.g. pesticide use, pollution, clearing, construction, aquaculture"
      )}

      <div className="md:col-span-2">
        {field(
          "Biodiversity / species observations",
          "species_observations",
          <textarea
            id="species_observations"
            rows={3}
            className={inputClass}
            placeholder="e.g. low bird and pollinator activity"
            value={value.species_observations ?? ""}
            onChange={(e) => set("species_observations", e.target.value)}
          />
        )}
      </div>
    </form>
  );
}
