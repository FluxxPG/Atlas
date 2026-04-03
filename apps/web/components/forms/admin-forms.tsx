"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { queueDiscoveryAction, queueGeoGridAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton({ label, pendingLabel }: { label: string; pendingLabel: string }) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? pendingLabel : label}
    </button>
  );
}

function StatusPill({ message, status }: { message?: string; status: "idle" | "success" | "error" }) {
  if (!message) {
    return null;
  }

  return (
    <div
      className={`rounded-3xl px-4 py-3 text-sm ${
        status === "success"
          ? "border border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
          : "border border-rose-400/30 bg-rose-500/10 text-rose-200"
      }`}
    >
      {message}
    </div>
  );
}

export function AdminDiscoveryForm() {
  const [state, action] = useFormState(queueDiscoveryAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="query"
          defaultValue="restaurants needing CRM"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Search discovery query"
        />
        <input
          name="city"
          defaultValue="Mumbai"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="City"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input
          name="region"
          defaultValue="Maharashtra"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Region"
        />
        <input
          name="country"
          defaultValue="India"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Country"
        />
        <select
          name="source"
          defaultValue="hybrid"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        >
          <option value="hybrid">Hybrid</option>
          <option value="public_web">Public Web</option>
          <option value="serpapi">SerpAPI</option>
          <option value="india_local">India Local Mix</option>
          <option value="google_business_profiles">Google Business Profile</option>
          <option value="google_maps">Google Maps</option>
          <option value="justdial">Justdial</option>
          <option value="sulekha">Sulekha</option>
          <option value="tracxn">Tracxn</option>
          <option value="indiamart">IndiaMART</option>
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="keywords"
          defaultValue="crm, automation, lead generation"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Keywords comma separated"
        />
        <input
          name="industries"
          defaultValue="Restaurants, Hospitality"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Industries comma separated"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input
          name="employee_range"
          defaultValue="1-50"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Employee range"
        />
        <input
          name="min_reviews"
          type="number"
          defaultValue="20"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Min reviews"
        />
        <input
          name="max_rating"
          type="number"
          step="0.1"
          defaultValue="3.5"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Max rating"
        />
        <select
          name="has_website"
          defaultValue=""
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        >
          <option value="">Website any</option>
          <option value="true">Has website</option>
          <option value="false">No website</option>
        </select>
      </div>
      <StatusPill message={state.message} status={state.status} />
      <SubmitButton label="Queue Discovery Job" pendingLabel="Queueing..." />
    </form>
  );
}

export function AdminGeoGridForm() {
  const [state, action] = useFormState(queueGeoGridAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="city"
          defaultValue="Bengaluru"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="City"
        />
        <input
          name="region"
          defaultValue="Karnataka"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Region"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input
          name="country"
          defaultValue="India"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Country"
        />
        <input
          name="latitude"
          type="number"
          step="0.0001"
          defaultValue="12.9716"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Latitude"
        />
        <input
          name="longitude"
          type="number"
          step="0.0001"
          defaultValue="77.5946"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Longitude"
        />
        <select
          name="source"
          defaultValue="hybrid"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        >
          <option value="hybrid">Hybrid</option>
          <option value="public_web">Public Web</option>
          <option value="serpapi">SerpAPI</option>
          <option value="india_local">India Local Mix</option>
          <option value="google_business_profiles">Google Business Profile</option>
          <option value="google_maps">Google Maps</option>
          <option value="justdial">Justdial</option>
          <option value="sulekha">Sulekha</option>
          <option value="tracxn">Tracxn</option>
          <option value="indiamart">IndiaMART</option>
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input
          name="keyword_set"
          defaultValue="restaurants, cafes, crm"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Keyword set comma separated"
        />
        <input
          name="industries"
          defaultValue="Hospitality, Food"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Industries comma separated"
        />
        <input
          name="radius_km"
          type="number"
          defaultValue="25"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Radius km"
        />
      </div>
      <StatusPill message={state.message} status={state.status} />
      <SubmitButton label="Queue Geo Grid Scan" pendingLabel="Queueing..." />
    </form>
  );
}
