"use client";

import { useEffect, useState } from "react";
import { Activity, Signal, Zap } from "lucide-react";

import { Card } from "@/components/ui/card";
import { WS_URL } from "@/lib/utils";

type FeedItem = {
  event: string;
  payload: Record<string, unknown>;
  timestamp: string;
};

const fallbackItems: FeedItem[] = [
  { event: "signal.created", payload: { company: "Acme Foods", signal: "low_rating" }, timestamp: "live" },
  { event: "opportunity.created", payload: { company: "Orbit Health", category: "automation_needs" }, timestamp: "live" },
  { event: "crawl.completed", payload: { city: "Bengaluru", records: 128 }, timestamp: "live" }
];

export function RealtimeFeed() {
  const [items, setItems] = useState<FeedItem[]>(fallbackItems);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data) as FeedItem;
      setItems((current) => [payload, ...current].slice(0, 6));
    };
    ws.onerror = () => ws.close();
    return () => ws.close();
  }, []);

  return (
    <Card className="h-full">
      <div className="mb-6 flex items-center gap-2 text-sm text-white">
        <Activity className="h-4 w-4 text-accent" />
        Realtime Platform Feed
      </div>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div
            key={`${item.event}-${index}`}
            className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200"
          >
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-400">
              {item.event.includes("signal") ? <Signal className="h-3.5 w-3.5" /> : <Zap className="h-3.5 w-3.5" />}
              {item.event}
            </div>
            <p>{JSON.stringify(item.payload)}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

