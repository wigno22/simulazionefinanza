import { Component } from '@angular/core';
import { StockListComponent } from './components/stock-list/stock-list.component';
import { PortfolioComponent } from './components/portfolio/portfolio.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [StockListComponent, PortfolioComponent],
  template: `
    <h1>TEST ROOT COMPONENT</h1>
    <stock-list></stock-list>
    <portfolio></portfolio>
  `
})
export class AppComponent {}
