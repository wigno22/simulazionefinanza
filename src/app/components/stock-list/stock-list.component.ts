import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarketService } from '../../services/market.service';
import { Stock } from '../../models/stock';

@Component({
  selector: 'stock-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stock-list.component.html'
})
export class StockListComponent implements OnInit {
  stocks: Stock[] = [];
  userId = 1;

  constructor(private marketService: MarketService) {}

  ngOnInit(): void {
    this.marketService.getStocks().subscribe(data => {
      this.stocks = data;
    });
  }

  buy(stock: Stock) {
    this.marketService.buyStock(this.userId, stock.id, 1).subscribe(() => {
      alert(`Acquistata 1 azione di ${stock.name}`);
    });
  }

  sell(stock: Stock) {
    this.marketService.sellStock(this.userId, stock.id, 1).subscribe(() => {
      alert(`Venduta 1 azione di ${stock.name}`);
    });
  }
}
