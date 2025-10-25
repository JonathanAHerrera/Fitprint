import axios from "axios";

const API_URL = "http://10.0.2.2:8000"; // update to your server

export interface ClothingItem {
  clothing_id: string;
  brand?: string;
  image_url: string;
  sustainability_score?: number;
  created_at?: string;
}

export const listItems = async (): Promise<ClothingItem[]> => {
  const res = await axios.get(`${API_URL}/items`);
  return res.data.items ?? [];
};

export const createItem = async (item: Partial<ClothingItem>) => {
  const res = await axios.post(`${API_URL}/items`, item);
  return res.data.item;
};

export const deleteItem = (clothing_id: string) => {
  return axios.delete(`${API_URL}/items/${clothing_id}`);
};
