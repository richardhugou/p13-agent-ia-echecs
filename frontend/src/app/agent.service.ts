import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

/** Réponse structurée de POST /api/v1/agent/ask — le dossier complet du graphe. */
export interface CoupTheorique {
  uci: string;
  san: string;
  /** Notation française annotée : « Fc5 (fou f8) » — pièce et case de départ explicites. */
  san_fr: string;
  games: number;
  white: number;
  draws: number;
  black: number;
}

export interface Video {
  video_id: string;
  titre: string;
  chaine: string;
  duree_s: number;
  url: string;
  embeddable: boolean;
}

export interface ReponseAgent {
  fen: string;
  answer: string;
  sources: string[];
  opening: { eco: string; name: string } | null;
  in_theory: boolean | null;
  total_games: number;
  theory_moves: CoupTheorique[];
  top_games: { white: string; black: string; year: number; winner: string | null }[];
  engine_eval: { cp: number | null; mate: number | null; depth: number; best_line: string[] } | null;
  rag_chunks: unknown[];
  videos: Video[];
  errors: string[];
}

/** L'API du POC — même hôte, port 8000 (CORS ouvert sur localhost:4200). */
const API = 'http://localhost:8000/api/v1';

@Injectable({ providedIn: 'root' })
export class AgentService {
  constructor(private http: HttpClient) {}

  ask(fen: string, question?: string): Observable<ReponseAgent> {
    return this.http.post<ReponseAgent>(`${API}/agent/ask`, { fen, question: question ?? null });
  }
}
