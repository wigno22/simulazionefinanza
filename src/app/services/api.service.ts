import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = '/api'; // Usa il proxy in sviluppo

  constructor(private http: HttpClient) {}

  // Esempio metodi per le tue API
  getPortfolio(): Observable<any> {
    return this.http.get(`${this.apiUrl}/portfolio`);
  }

  addTransaction(transaction: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/transactions`, transaction);
  }

  getInvestments(): Observable<any> {
    return this.http.get(`${this.apiUrl}/investments`);
  }
}
