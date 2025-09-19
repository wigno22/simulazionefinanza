import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarketService } from '../../services/market.service';
import { Portfolio } from '../../models/portfolio';

@Component({
  selector: 'portfolio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './portfolio.component.html'
})
export class PortfolioComponent implements OnInit {
  portfolio: Portfolio | null = null;
  userId = 1;

  constructor(private marketService: MarketService) {}

  ngOnInit(): void {
    this.marketService.getPortfolio(this.userId).subscribe(data => {
      this.portfolio = data;
    });
  }
}
