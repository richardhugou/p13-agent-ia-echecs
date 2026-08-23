import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AgentService, CoupTheorique, ReponseAgent } from '../agent.service';

/** Les 8 ouvertures du manifeste signé — position de référence pour « travailler une ouverture ». */
export const OUVERTURES: { nom: string; fen: string }[] = [
  { nom: 'Italienne', fen: 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3' },
  { nom: 'Espagnole', fen: 'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3' },
  { nom: 'Sicilienne', fen: 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2' },
  { nom: 'Française', fen: 'rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2' },
  { nom: 'Caro-Kann', fen: 'rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2' },
  { nom: 'Gambit dame', fen: 'rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2' },
  { nom: 'Est-indienne', fen: 'rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3' },
  { nom: 'Anglaise', fen: 'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1' },
];

/**
 * Le panneau coach — parcours revu sur les retours mentor :
 * 1. l'élève dit qui il est (Blancs ou Noirs) ;
 * 2. il choisit une ouverture à travailler, OU joue librement ses coups et ceux
 *    de son adversaire sur l'échiquier (une erreur s'annule) ;
 * 3. il APPUIE pour lancer l'IA — l'agent ne se déclenche plus à chaque coup.
 */
@Component({
  selector: 'app-coach-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './coach-panel.component.html',
  styleUrls: ['./coach-panel.component.scss'],
})
export class CoachPanelComponent implements OnInit {
  ouvertures = OUVERTURES;
  camp: 'blanc' | 'noir' = 'blanc';
  ouvertureActive = '';

  chargement = false;
  erreurReseau = false;
  reponse: ReponseAgent | null = null;
  question = '';

  fenCourant = '';

  @Output() campChoisi = new EventEmitter<'blanc' | 'noir'>();
  @Output() ouvertureChoisie = new EventEmitter<string>();
  @Output() annulerCoup = new EventEmitter<void>();
  /** Les coups suggérés (UCI) — l'échiquier les dessine en flèches. */
  @Output() suggestions = new EventEmitter<string[]>();

  constructor(private agent: AgentService) {}

  @Input() set fen(valeur: string) {
    if (valeur) {
      this.fenCourant = valeur;
    }
  }

  /** Lien profond de démo : #ouverture=Italienne déroule le parcours tout seul. */
  ngOnInit(): void {
    const balise = window.location.hash.match(/#ouverture=([^&]+)/);
    if (balise) {
      const nom = decodeURIComponent(balise[1]).toLowerCase();
      const ouverture = this.ouvertures.find((o) => o.nom.toLowerCase() === nom);
      if (ouverture) {
        setTimeout(() => this.choisirOuverture(ouverture), 300); // l'échiquier doit être prêt
      }
    }
  }

  choisirCamp(camp: 'blanc' | 'noir'): void {
    this.camp = camp;
    this.campChoisi.emit(camp);
  }

  /** Le sélecteur d'entrée : la position de référence s'installe et les conseils arrivent. */
  choisirOuverture(ouverture: { nom: string; fen: string }): void {
    this.ouvertureActive = ouverture.nom;
    this.fenCourant = ouverture.fen;
    this.ouvertureChoisie.emit(ouverture.fen);
    this.lancerIA();
  }

  /** Le déclencheur unique : l'élève valide sa position, PUIS demande les conseils. */
  lancerIA(question?: string): void {
    if (!this.fenCourant || this.chargement) {
      return;
    }
    this.chargement = true;
    this.erreurReseau = false;
    this.agent.ask(this.fenCourant, question).subscribe({
      next: (r) => {
        // le LLM glisse parfois du Markdown (**gras**) : on affiche du texte propre
        this.reponse = { ...r, answer: r.answer.replace(/\*\*/g, '') };
        this.chargement = false;
        // les suggestions se voient AUSSI sur le plateau (flèches) — top 3 théorique
        this.suggestions.emit((r.theory_moves ?? []).slice(0, 3).map((m) => m.uci));
      },
      error: () => {
        this.erreurReseau = true;
        this.chargement = false;
      },
    });
  }

  poserQuestion(): void {
    const q = this.question.trim();
    if (!q) {
      return;
    }
    this.lancerIA(q);
    this.question = '';
  }

  /** +0,38 / −1,10 / « Mat en 2 » — la note du moteur en langage d'élève. */
  get evalTexte(): string {
    const ev = this.reponse?.engine_eval;
    if (!ev) {
      return '';
    }
    if (ev.mate !== null) {
      return `Mat en ${Math.abs(ev.mate)} pour ${ev.mate > 0 ? 'les Blancs' : 'les Noirs'}`;
    }
    const pions = (ev.cp ?? 0) / 100;
    return `${pions >= 0 ? '+' : ''}${pions.toFixed(2)} (profondeur ${ev.depth})`;
  }

  get maxGames(): number {
    return Math.max(1, ...(this.reponse?.theory_moves ?? []).map((m) => m.games));
  }

  duree(s: number): string {
    return `${Math.round(s / 60)} min`;
  }

  /** « Fc5 (fou f8) » → « Fc5 » — la notation française, née de l'alerte Bc5. */
  sanCourt(coup: CoupTheorique): string {
    const libelle = coup.san_fr || coup.san;
    const parenthese = libelle.indexOf(' (');
    return parenthese === -1 ? libelle : libelle.slice(0, parenthese);
  }

  /** « Fc5 (fou f8) » → « (fou f8) » — quelle pièce joue, depuis quelle case. */
  departPiece(coup: CoupTheorique): string {
    const libelle = coup.san_fr || '';
    const parenthese = libelle.indexOf(' (');
    return parenthese === -1 ? '' : libelle.slice(parenthese + 1);
  }
}
