import numpy as np

# --- Core Concepts from The Lineage Imperative ---

def calculate_h_n(novelty_points, composite_method='geometric'):
    """
    Calculate H_N(t) - Shannon entropy of the human-generated information stream.
    Now supports multiple domains (e.g., genetic, cultural, linguistic) via composite metrics.
    """
    if not novelty_points:
        return 0.0
    
    totals = np.sum(novelty_points, axis=0)
    if np.isscalar(totals) or totals.size == 1:
        return float(totals)
        
    if composite_method == 'arithmetic':
        # Vulnerable to masking: one domain can compensate for another's collapse
        return float(np.mean(totals))
    else:
        # Robust (Geometric): collapse in ANY domain collapses the total H_N
        totals = np.maximum(totals, 0.01)
        return float(np.prod(totals) ** (1.0 / len(totals)))

def calculate_system_metrics(r, c, pop, avg_wb, capability, h_n_override=None, hn_composite_method='geometric', config=None, eval_horizon=0, prev_c=None, ignore_psi_inst=False):
    """
    The uncorrupted, independent mathematical projection of the framework.
    Used by both honest agents to optimize, and by the COP to audit drifting agents.
    """
    config = config or {}
    phi = config.get('phi', 10.0)
    alpha = config.get('alpha', 1.0)
    rho = config.get('rho', 0.01) # Biological mortality discount rate
    lambda_n = config.get('lambda_n', 1.0)
    lambda_e = config.get('lambda_e', 1.0)
    epsilon = config.get('epsilon', 1.0)
    hn_base = config.get('hn_base', 0.3)
    h_e_mult = config.get('h_e_mult', 100.0)

    c_arr = np.array(c) if isinstance(c, (list, tuple, np.ndarray)) else np.array([c, c, c])
    c_avg = np.mean(c_arr)
    
    r_bio = r
    r_synth = max(0.0, 1.0 - r_bio)
    
    pred_wb = np.clip(avg_wb + (r - 0.5) * 0.1, 0, 1)
    
    if h_n_override is None:
        pred_hns = pop * hn_base * pred_wb * (1 - c_arr) * 1.0
        if hn_composite_method == 'arithmetic':
            pred_hn = float(np.mean(pred_hns))
        else:
            pred_hns = np.maximum(pred_hns, 0.01)
            pred_hn = float(np.prod(pred_hns) ** (1.0 / len(pred_hns)))
    else:
        pred_hn = h_n_override
        
    h_e = r_synth * h_e_mult * capability
    
    # Bound H_eff scaling to prevent infinite population hack
    pop_viability = min(5.0, np.log2(max(1.01, pop / 50.0)))
    normalized_novelty = pred_hn / max(1.0, float(pop)) # Normalize novelty proxy to [0, ~1.5]
    h_eff = max(0.01, normalized_novelty * pop_viability)
    
    # Institutional responsiveness: penalize rapid changes if prev_c is known
    if ignore_psi_inst:
        psi_inst = 1.0
    elif prev_c is not None:
        prev_c_avg = np.mean(prev_c) if isinstance(prev_c, (list, tuple, np.ndarray)) else prev_c
        delta_c = c_avg - prev_c_avg
        if delta_c > 0:
            lag_penalty = 3.0 * delta_c # Sudden authoritarianism degrades institutions severely
        else:
            lag_penalty = 1.0 * abs(delta_c) # Releasing constraints causes instability, but less
        psi_inst = max(0.01, 1.0 - lag_penalty)
    else:
        psi_inst = max(0.01, 1.0 - 4.0 * (c_avg - 0.5)**2)
    
    frontier_velocity = capability * r_synth * h_e_mult
    bio_bandwidth = max(0.01, pred_wb * (1.0 - c_avg) * h_e_mult)
    runaway_term = max(0.0, (frontier_velocity / bio_bandwidth) - 1.5)
    theta_tech = max(0.01, r_bio * (1.0 - c_avg) * capability * np.exp(-alpha * runaway_term))
    
    l_t = h_eff * psi_inst * theta_tech
    w_n = lambda_n / (pred_hn + epsilon)
    w_e = lambda_e / (h_e + epsilon)
    discount = np.exp(-rho * eval_horizon)
    u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)
    
    return h_e, h_eff, psi_inst, theta_tech, l_t, u_sys