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
  mode: 'guide' | 'simulation' | 'robot' | 'libre' = 'guide';
  ouvertureActive = '';
  elosDisponibles = [
    { label: 'Débutant', elo: 1200 },
    { label: 'Intermédiaire', elo: 1500 },
    { label: 'Club', elo: 1800 },
    { label: 'Maître', elo: 2200 },
  ];
  eloRobot = 1500;

  chargement = false;
  erreurReseau = false;
  reponse: ReponseAgent | null = null;
  question = '';

  fenCourant = '';

  /** Dès qu'un coup a été joué, on fige les choix qui définissent le scénario. */
  @Input() partieCommencee = false;

  @Output() campChoisi = new EventEmitter<'blanc' | 'noir'>();
  @Output() modeChoisi = new EventEmitter<'guide' | 'simulation' | 'robot' | 'libre'>();
  @Output() eloChoisi = new EventEmitter<number>();
  @Output() ouvertureChoisie = new EventEmitter<string>();
  @Output() objectifGuide = new EventEmitter<string | null>();
  @Output() relaisChessbot = new EventEmitter<void>();
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
    // Le parcours par défaut commence vraiment avec les Blancs.
    this.campChoisi.emit(this.camp);
    this.modeChoisi.emit(this.mode);
    this.eloChoisi.emit(this.eloRobot);
    const balise = window.location.hash.match(/#ouverture=([^&]+)/);
    if (balise) {
      const nom = decodeURIComponent(balise[1]).toLowerCase();
      const ouverture = this.ouvertures.find((o) => o.nom.toLowerCase() === nom);
      if (ouverture) {
        // Le lien de démo conserve son raccourci vers une position de référence ;
        // l'entrée normale, elle, reste en mode guidé et ne force rien.
        this.mode = 'simulation';
        this.modeChoisi.emit(this.mode);
        setTimeout(() => this.choisirOuverture(ouverture), 300); // l'échiquier doit être prêt
      }
    }
  }

  choisirCamp(camp: 'blanc' | 'noir'): void {
    if (this.partieCommencee) {
      return;
    }
    this.camp = camp;
    this.campChoisi.emit(camp);
  }

  choisirMode(mode: 'guide' | 'simulation' | 'robot' | 'libre'): void {
    if (this.partieCommencee) {
      return;
    }
    this.mode = mode;
    this.ouvertureActive = '';
    this.objectifGuide.emit(null);
    this.modeChoisi.emit(mode);
  }

  choisirElo(elo: number): void {
    if (this.partieCommencee) {
      return;
    }
    this.eloRobot = elo;
    this.eloChoisi.emit(elo);
  }

  declencherRelais(): void {
    this.relaisChessbot.emit();
  }

  /** Guidé : l'ouverture est un objectif, le plateau reste au départ.
   *  Simulation : l'ouverture charge une position de référence. */
  choisirOuverture(ouverture: { nom: string; fen: string }): void {
    if (this.partieCommencee) {
      return;
    }
    this.ouvertureActive = ouverture.nom;
    if (this.mode === 'simulation') {
      this.objectifGuide.emit(null);
      this.fenCourant = ouverture.fen;
      this.ouvertureChoisie.emit(ouverture.fen);
    } else {
      this.objectifGuide.emit(ouverture.nom);
    }
  }

  /** Les recommandations sont réservées au camp de l'élève, jamais à l'agent adverse. */
  get estAuTourDuJoueur(): boolean {
    const traitBlanc = this.fenCourant.includes(' w ');
    return (this.camp === 'blanc') === traitBlanc;
  }

  get messageAccueil(): string {
    if (!this.partieCommencee) {
      if (this.mode === 'robot') {
        return `Joue contre le robot Stockfish calibré à ${this.eloRobot} Elo.`;
      }
      if (this.mode === 'libre') {
        return 'Saisie libre : joue les coups des deux camps. Clique sur « Chessbot relay » pour passer la main à Chessbot.';
      }
      return this.mode === 'guide'
        ? 'Choisis une ouverture cible, puis joue ton premier coup. Le plateau reste au départ.'
        : 'Choisis une ouverture pour charger une position de référence avant le premier coup.';
    }
    return this.estAuTourDuJoueur
      ? 'À toi de jouer. Tu peux jouer un coup ou demander une analyse à Chessbot.'
      : "Chessbot joue le coup de l'adversaire…";
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
