// src/app/app.component.ts (CORRETTO)

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  // Usa un template inline che contiene solo il router-outlet
  template: '<router-outlet></router-outlet>'
})
export class AppComponent {
  title = 'simulazionefinanza';
}
