import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SMARTInput:
    alternatives: List[str]
    criteria: List[str]
    performance: np.ndarray
    weights_raw: np.ndarray
    types: List[str]
    weight_method: str

class SMARTEngine:
    @staticmethod
    def compute_weights(weights_raw: np.ndarray, method: str) -> np.ndarray:
        w_raw = np.atleast_1d(np.asarray(weights_raw, dtype=float))
        n = len(w_raw)
        
        if method == 'equal':
            return np.full(n, 1.0 / n)
            
        elif method == 'roc':
            roc_standard = np.zeros(n)
            for k in range(1, n + 1):
                roc_standard[k-1] = (1 / n) * sum(1 / j for j in range(k, n + 1))
            
            weights = np.zeros(n)
            for i, r in enumerate(w_raw):
                r_idx = int(r) - 1
                if 0 <= r_idx < n:
                    weights[i] = roc_standard[r_idx]
                else:
                    weights[i] = 1.0 / n
            if weights.sum() > 0:
                return weights / weights.sum()
            return np.full(n, 1.0 / n)
            
        else: # direct / swing
            total = w_raw.sum()
            if total == 0: return np.full(n, 1.0 / n)
            return w_raw / total

    @staticmethod
    def compute_utility(performance: np.ndarray, types: List[str]) -> np.ndarray:
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
        weights = self.compute_weights(data.weights_raw, data.weight_method)
        U = self.compute_utility(data.performance, data.types)
        
        # Matriks Agregasi
        aggregation_matrix = U * weights
        
        scores = np.atleast_1d(U @ weights)
        ranking = np.argsort(scores)[::-1].tolist()
        
        return {
            "normalized_weights": weights.tolist(),
            "utility_matrix": U.tolist(),
            "aggregation_matrix": aggregation_matrix.tolist(),
            "final_scores": scores.tolist(),
            "ranking_indices": ranking,
            "ranked_alternatives": [data.alternatives[i] for i in ranking]
        }

    def run_oat_sensitivity(self, data: SMARTInput, target_idx: int, steps=30):
        w_base = self.compute_weights(data.weights_raw, data.weight_method)
        weight_vals = np.linspace(0.0, 1.0, steps)
        scores_history = []
        
        for wk in weight_vals:
            w_new = w_base.copy()
            if target_idx >= len(w_base): target_idx = 0
            remaining = 1.0 - float(w_base[target_idx])
            
            if remaining > 1e-9:
                for j in range(len(w_base)):
                    if j != target_idx:
                        w_new[j] = float(w_base[j]) * (1.0 - wk) / remaining
            else:
                n_other = len(w_base) - 1
                if n_other > 0:
                    for j in range(len(w_base)):
                        if j != target_idx: w_new[j] = (1.0 - wk) / n_other
            w_new[target_idx] = wk
            
            U = self.compute_utility(data.performance, data.types)
            scores_history.append(np.atleast_1d(U @ w_new).tolist())
            
        return weight_vals.tolist(), scores_history