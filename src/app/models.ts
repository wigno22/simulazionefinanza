export interface Position {
  symbol: string;
  name: string;
  quantity: number;
  price: number;
  value: number;
}

export interface Portfolio {
  username: string;
  balance: number;
  positions: Position[];
}

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  drift?: number;
  volatility?: number;
}
