"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const suggestedQueries = [
  "fast growing startups",
  "companies needing CRM",
  "restaurants with bad reviews",
  "manufacturers hiring operations managers"
];

export function SearchConsole({ initialQuery }: { initialQuery?: string }) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery || suggestedQueries[0]);

  const runSearch = () => {
    router.push(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-aurora opacity-70" />
      <div className="relative">
        <div className="mb-5 flex items-center gap-2 text-accent">
          <Sparkles className="h-4 w-4" />
          <span className="text-xs uppercase tracking-[0.25em]">AI Intelligence Search</span>
        </div>
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="flex flex-1 items-center gap-3 rounded-full border border-white/10 bg-slate-950/40 px-5 py-4">
            <Search className="h-4 w-4 text-slate-400" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  runSearch();
                }
              }}
              className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
              placeholder="Ask for opportunities, signals, cities, or technologies"
            />
          </div>
          <Button onClick={runSearch}>Run Search</Button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {suggestedQueries.map((item) => (
            <button
              key={item}
              onClick={() => {
                setQuery(item);
                router.push(`/search?q=${encodeURIComponent(item)}`);
              }}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/10 hover:text-white"
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </Card>
  );
}
