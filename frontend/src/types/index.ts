/**
 * Frontend types and interfaces
 */

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Prediction {
  id: number;
  user_id?: number;
  title?: string;
  description?: string;
  region?: string;
  address?: string;
  city?: string;
  metro?: string;
  street_type?: string;
  district?: string;
  square?: number;
  rooms_clean?: number;
  floor?: number;
  max_floor?: number;
  time_to_metro?: number;
  latitude?: number;
  longitude?: number;
  // backend may return one of these fields for price
  predicted_price?: number;
  prediction?: number;
  price?: number;
  estimated_price?: number;
  confidence_score?: number;
  images?: Image[];
  created_at?: string;
  updated_at?: string;
}

export interface Image {
  id: number;
  prediction_id: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  created_at: string;
}

export interface PredictionCreate {
  title: string;
  description?: string;
  region: string;
  city: string;
  metro: string;
  street_type: string;
  square: number;
  rooms_clean: number;
  floor: number;
  max_floor: number;
  time_to_metro?: number;
  has_furniture?: boolean;
  has_appliances?: boolean;
  has_tv?: boolean;
  has_wifi?: boolean;
  has_dishwasher?: boolean;
  has_washing_machine?: boolean;
  has_parking?: boolean;
  has_balcony?: boolean;
  has_security?: boolean;
  renovation_euro?: boolean;
  renovation_cosmetic?: boolean;
  renovation_new?: boolean;
  pets_allowed?: boolean;
  children_allowed?: boolean;
  is_new_building?: boolean;
  is_first_floor?: boolean;
  is_last_floor?: boolean;
  floor_category?: string;
  building_height?: string;
  size_category?: string;
  metro_accessibility?: string;
  district?: string;
  latitude?: number;
  longitude?: number;
}


export interface Analytics {
  total_predictions: number;
  price_stats: {
    min_price: number;
    max_price: number;
    avg_price: number;
    median_price: number;
    count: number;
  };
  by_district: Array<{
    district: string;
    avg_price: number;
    count: number;
  }>;
}
