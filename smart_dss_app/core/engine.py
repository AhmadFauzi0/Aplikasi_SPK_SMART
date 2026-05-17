# core/engine.py
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SMARTInput:
    alternatives: List[str]
    criteria: List[str]
    performance: np.ndarray
    weights_raw: np.ndarray
    types: List[str]  # 'benefit' atau 'cost'

class SMARTEngine:
    @staticmethod
    def compute_roc_weights(n: int) -> np.ndarray:
        w = np.zeros(n)
        for k in range(1, n + 1):
            w[k-1] = (1 / n) * sum(1 / j for j in range(k, n + 1))
        return w

    @staticmethod
    def normalize_weights(w_raw: np.ndarray) -> np.ndarray:
        # PENGAMAN: Pastikan bobot minimal 1 Dimensi
        w = np.atleast_1d(np.asarray(w_raw, dtype=float))
        total = w.sum()
        if total == 0: raise ValueError("Total bobot tidak boleh nol.")
        return w / total

    @staticmethod
    def compute_utility(performance: np.ndarray, types: List[str]) -> np.ndarray:
        # PENGAMAN: Pastikan matriks minimal 2 Dimensi (meski cuma 1 alternatif & 1 kriteria)
        X = np.atleast_2d(np.asarray(performance, dtype=float))
        U = np.zeros_like(X)
        for j, ctype in enumerate(types):
            col = X[:, j]
            x_min, x_max = col.min(), col.max()
            if x_max == x_min:
                U[:, j] = 0.5  
                continue
            
            if ctype.lower() == 'benefit':
                U[:, j] = (col - x_min) / (x_max - x_min)
            else:
                U[:, j] = (x_max - col) / (x_max - x_min)
        return U

    def calculate(self, data: SMARTInput) -> Dict[str, Any]:
        weights = self.normalize_weights(data.weights_raw)
        U = self.compute_utility(data.performance, data.types)
        
        # PENGAMAN: Hasil dot product pastikan minimal 1 Dimensi
        scores = np.atleast_1d(U @ weights)  
        ranking = np.argsort(scores)[::-1].tolist()
        
        return {
            "utility_matrix": U.tolist(),
            "final_scores": scores.tolist(),
            "normalized_weights": weights.tolist(),
            "ranking_indices": ranking,
            "ranked_alternatives": [data.alternatives[i] for i in ranking]
        }

    def run_oat_sensitivity(self, data: SMARTInput, target_idx: int, steps=30):
        w_base = self.normalize_weights(data.weights_raw)
        weight_vals = np.linspace(0.0, 1.0, steps)
        scores_history = []
        
        for wk in weight_vals:
            w_new = w_base.copy()
            # PENGAMAN: Konversi ke float biasa untuk hindari error skalar NumPy
            remaining = 1.0 - float(w_base[target_idx]) 
            
            if remaining > 1e-9:
                for j in range(len(w_base)):
                    if j != target_idx:
                        w_new[j] = float(w_base[j]) * (1.0 - wk) / remaining
            w_new[target_idx] = wk
            
            U = self.compute_utility(data.performance, data.types)
            
            # PENGAMAN: Pastikan masuk ke history sebagai Array 1D yang diubah ke list
            safe_scores = np.atleast_1d(U @ w_new).tolist()
            scores_history.append(safe_scores)
            
        return weight_vals.tolist(), scores_history