import { CommonModule } from '@angular/common';
import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, tap } from 'rxjs/operators';

import { AgentService, ReponseAgent } from '../agent.service';

/**
 * Le panneau coach — la moitié droite de la maquette :
 * badge en/hors théorie, coups des maîtres avec stats, réponse sourcée, vidéos.
 * Reçoit le FEN de l'échiquier ; débounce 400 ms pour épargner l'API.
 */
@Component({
  selector: 'app-coach-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './coach-panel.component.html',
  styleUrls: ['./coach-panel.component.scss'],
})
export class CoachPanelComponent implements OnInit, OnDestroy {
  private fenSubject = new Subject<string>();
  private abonnement?: Subscription;
  private fenCourant = '';

  chargement = false;
  erreurReseau = false;
  reponse: ReponseAgent | null = null;
  question = '';

  constructor(private agent: AgentService) {}

  @Input() set fen(valeur: string) {
    if (valeur) {
      this.fenCourant = valeur;
      this.fenSubject.next(valeur);
    }
  }

  ngOnInit(): void {
    this.abonnement = this.fenSubject
      .pipe(
        debounceTime(400),
        distinctUntilChanged(),
        tap(() => {
          this.chargement = true;
          this.erreurReseau = false;
        }),
        switchMap((fen) => this.agent.ask(fen)),
      )
      .subscribe({
        next: (r) => {
          this.reponse = r;
          this.chargement = false;
        },
        error: () => {
          this.erreurReseau = true;
          this.chargement = false;
          this.ngOnInit(); // ré-arme le flux après une erreur réseau
        },
      });
    if (this.fenCourant) {
      this.fenSubject.next(this.fenCourant); // le FEN initial arrive avant ngOnInit : on le rejoue
    }
  }

  ngOnDestroy(): void {
    this.abonnement?.unsubscribe();
  }

  poserQuestion(): void {
    const q = this.question.trim();
    if (!q || !this.fenCourant) {
      return;
    }
    this.chargement = true;
    this.agent.ask(this.fenCourant, q).subscribe({
      next: (r) => {
        this.reponse = r;
        this.chargement = false;
        this.question = '';
      },
      error: () => {
        this.erreurReseau = true;
        this.chargement = false;
      },
    });
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
}
