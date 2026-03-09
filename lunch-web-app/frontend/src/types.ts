export interface MenuItem {
  name: string;
  price: number | null;
  category: string;
  description: string | null;
}

export interface Order {
  name: string;
  items: string[];
  submitted_at: string;
}

export interface LunchSession {
  id: string;
  restaurant_name: string;
  description: string | null;
  items: MenuItem[];
  orders: Record<string, Order>;
  created_at: string;
}
