import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Stock } from '../models/stock';
import { Portfolio } from '../models/portfolio';

@Injectable({ providedIn: 'root' })
export class MarketService {
  private apiUrl = 'http://localhost:3000'; // backend Node

  constructor(private http: HttpClient) {}

  getStocks(): Observable<Stock[]> {
    return this.http.get<Stock[]>(`${this.apiUrl}/stocks`);
  }

  buyStock(userId: number, stockId: number, quantity: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/buy`, { userId, stockId, quantity });
  }

  sellStock(userId: number, stockId: number, quantity: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/sell`, { userId, stockId, quantity });
  }

  getPortfolio(userId: number): Observable<Portfolio> {
    return this.http.get<Portfolio>(`${this.apiUrl}/users/${userId}/portfolio`);
  }
}
