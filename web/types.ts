/** One recommendation = grounded place fields + LLM reason. */
export type Rec = {
  place_id: string;
  name: string;
  lat: number;
  lng: number;
  rating: number;
  distance_m: number;
  open_now: boolean;
  price_level: number;
  category?: string;
  reason: string;
};

export type RecommendResponse = {
  recommendations: Rec[];
  grounded: boolean;
  message?: string | null;
  intent?: {
    area?: string;
    category?: string;
    radius_m?: number;
    constraints?: string[];
  };
};
