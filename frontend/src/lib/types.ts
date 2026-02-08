// API response types

export interface GraphStats {
  nodes: Record<string, number>;
  edges: Record<string, number>;
  reachable_remedies: number;
}

export interface MappedSymptom {
  extracted_name: string;
  category: string;
  matched_id: string | null;
  matched_name: string | null;
}

export interface RankedRemedy {
  remedy: string;
  score: number;
  rubric_hits: number;
  details: Array<{
    symptom_id: string;
    rubric: string;
    grade: number;
  }>;
  mean_score?: number;
  confidence_interval?: [number, number];
  rank_stability?: number;
}

export interface ReliabilityResult {
  reliability_score: number;
  alerts: string[];
  suggestion?: string;
  contradictions?: Array<{
    symptom_a: string;
    symptom_b: string;
    strength: number;
  }>;
}

export interface UncertaintyResult {
  overall_certainty: number;
  remedies: Array<{
    remedy: string;
    mean_score: number;
    confidence_interval: [number, number];
    rank_stability: number;
  }>;
}

export interface PatternDiscovery {
  description: string;
  frequency: number;
  success_rate: number;
  remedy?: string;
}

export interface ConsultResult {
  symptom_ids: string[];
  ranked_remedies: RankedRemedy[];
  reliability?: ReliabilityResult;
  uncertainty?: UncertaintyResult;
  rare_patterns?: PatternDiscovery[];
  explanation?: string;
  elapsed_seconds?: number;
}

export interface RemedyDetail {
  abbrev: string;
  name: string;
  common_name: string;
  source: string | null;
  indications_count: number;
  relationships: Array<{
    type: string;
    target: string;
    target_abbrev: string;
  }>;
  top_rubrics: Array<{
    rubric: string;
    grade: number;
  }>;
}

export interface SearchResult {
  abbrev: string;
  name: string;
  common_name: string;
}

export interface NetworkData {
  nodes: Array<{ id: string; name: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
}
