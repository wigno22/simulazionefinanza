import { Position } from './position';

export interface Portfolio {
  id: number;
  username: string;
  balance: number;
  positions: Position[];
}
