import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Change to your server URL in production

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for AI processing
});

export interface OutfitAnalysisRequest {
  user_id: string;
  image: File;
}

export interface CategoryScore {
  score: number;
  description: string;
}

export interface Categories {
  material_origin: CategoryScore;
  production_impact: CategoryScore;
  labor_ethics: CategoryScore;
  end_of_life: CategoryScore;
  brand_transparency: CategoryScore;
}

export interface RegionalAlerts {
  EU?: string;
  CA?: string;
  US?: string;
  UK?: string;
}

export interface SustainabilityReport {
  clothing_id: string;
  report_id: string;
  brand: string;
  categories: Categories;
  overall_score: number;
  overall_description: string;
  regional_alerts: RegionalAlerts;
  alternative_ids: string[];
  created_at: string;
}

export interface AlternativeProduct {
  alternative_id: string;
  name: string;
  brand: string;
  image_url: string;
  sustainability_score: number;
  link: string;
  why_sustainable: string;
  clothing_id: string;
}

export interface ClothingResponse {
  clothing_id: string;
  brand: string;
  image_file: string;
  created_at?: string;
  updated_at?: string;
}

export interface OutfitAnalysisResponse {
  clothing_item: ClothingResponse;
  sustainability_report: SustainabilityReport;
  alternatives: AlternativeProduct[];
  analysis_id: string;
  created_at: string;
}

export const apiService = {
  async analyzeOutfit(userId: string, imageUri: string): Promise<OutfitAnalysisResponse> {
    const formData = new FormData();
    formData.append('user_id', userId);
    
    // Convert image URI to blob for upload
    const response = await fetch(imageUri);
    const blob = await response.blob();
    formData.append('image', blob as any, 'image.jpg');

    console.log('Sending request to backend...');
    const { data } = await api.post<OutfitAnalysisResponse>('/analysis/outfit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('Received response from backend:', data);
    return data;
  },

  async getUserAnalyses(userId: string): Promise<OutfitAnalysisResponse[]> {
    const { data } = await api.get<OutfitAnalysisResponse[]>(`/analysis/outfit/user/${userId}`);
    return data;
  },

  async getAnalysis(analysisId: string): Promise<OutfitAnalysisResponse> {
    const { data } = await api.get<OutfitAnalysisResponse>(`/analysis/outfit/${analysisId}`);
    return data;
  },
};
