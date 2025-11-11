// store/useStore.ts


import { create } from 'zustand';
import { User, Dataset } from '@/types';

interface AppState {
  user: User | null;
  currentDataset: Dataset | null;
  datasets: Dataset[];
  setUser: (user: User | null) => void;
  setCurrentDataset: (dataset: Dataset | null) => void;
  setDatasets: (datasets: Dataset[]) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  currentDataset: null,
  datasets: [],
  setUser: (user) => set({ user }),
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
  setDatasets: (datasets) => set({ datasets }),
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, currentDataset: null, datasets: [] });
  },
}));