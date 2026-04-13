export interface MenuItem {
  name: string;
  price: number | null;
  category: string;
  description: string;
  subcategory: string | null;
}

export interface RestaurantMenu {
  restaurant_name: string;
  items: MenuItem[];
}

export interface Order {
  name: string;
  items: string[];
  submitted_at: string;
}

export interface LunchSession {
  id: string;
  title: string;
  restaurants: RestaurantMenu[];
  description: string | null;
  orders: Record<string, Order>;
  created_at: string;
}
