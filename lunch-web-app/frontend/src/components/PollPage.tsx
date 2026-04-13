import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Card,
  Text,
  Input,
  Button,
  Checkbox,
  Spinner,
  Badge,
  Divider,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { Food24Regular, Send24Regular } from "@fluentui/react-icons";
import { getSession, submitOrder } from "../api";
import { useSSE } from "../hooks/useSSE";
import type { LunchSession, MenuItem, RestaurantMenu } from "../types";
import OrderList from "./OrderList";
import CsvButton from "./CsvButton";

// Nexer brand colors per restaurant name (falls back to cycling palette)
const RESTAURANT_COLORS: Record<string, { bg: string; header: string }> = {
  "Holy Greens": { bg: "#D9E6F0", header: "#190878" },
  "Dockside Burgers": { bg: "#FFE8DE", header: "#FF875A" },
};
const FALLBACK_COLORS = [
  { bg: "#F0E6FF", header: "#AA4BF5" },
  { bg: "#EDE0FF", header: "#5A1EA0" },
  { bg: "#F0F0F0", header: "#919191" },
];

function getColor(name: string, index: number) {
  return RESTAURANT_COLORS[name] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

const useStyles = makeStyles({
  page: {
    minHeight: "100vh",
    backgroundColor: "#F0F0F0",
  },
  topBar: {
    backgroundColor: "#190878",
    padding: "12px 24px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  topBarText: {
    color: "white",
    fontSize: "16px",
    fontWeight: 600,
  },
  content: {
    maxWidth: "720px",
    margin: "24px auto",
    padding: "0 16px",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  card: { padding: "24px" },
  nameRow: {
    display: "flex",
    gap: "12px",
    alignItems: "end",
    marginBottom: "16px",
  },
  restaurantSection: {
    borderRadius: "10px",
    overflow: "hidden",
    marginBottom: "8px",
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  restaurantHeader: {
    padding: "10px 16px",
  },
  restaurantBody: {
    padding: "12px 16px",
  },
  category: {
    marginTop: "12px",
    marginBottom: "4px",
    textTransform: "capitalize",
  },
  item: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "6px 0",
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  itemLeft: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    flex: 1,
  },
  price: { fontWeight: 600, whiteSpace: "nowrap" as const },
  actions: {
    display: "flex",
    gap: "12px",
    marginTop: "16px",
    alignItems: "center",
  },
  successBanner: {
    padding: "12px 16px",
    backgroundColor: "#D9E6F0",
    borderRadius: "8px",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  center: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
  },
});

const CATEGORY_ORDER = ["main", "side", "drink", "dessert", "other"];

// Flat item with restaurant context for selection tracking
interface FlatItem extends MenuItem {
  globalIdx: number;
  restaurantName: string;
}

function flattenItems(restaurants: RestaurantMenu[]): FlatItem[] {
  const result: FlatItem[] = [];
  restaurants.forEach((r) => {
    r.items.forEach((item) => {
      result.push({ ...item, globalIdx: result.length, restaurantName: r.restaurant_name });
    });
  });
  return result;
}

export default function PollPage() {
  const { id } = useParams<{ id: string }>();
  const styles = useStyles();
  const [session, setSession] = useState<LunchSession | null>(null);
  const [error, setError] = useState("");
  const [name, setName] = useState(() => localStorage.getItem("lunch_name") || "");
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!id) return;
    getSession(id).then(setSession).catch(() => setError("Session not found"));
  }, [id]);

  const handleSSEUpdate = useCallback((data: LunchSession) => {
    setSession(data);
  }, []);

  useSSE(id, handleSSEUpdate);

  if (error) {
    return (
      <div className={styles.center}>
        <Text size={500}>{error}</Text>
      </div>
    );
  }
  if (!session) {
    return (
      <div className={styles.center}>
        <Spinner size="large" label="Loading..." />
      </div>
    );
  }

  const flatItems = flattenItems(session.restaurants ?? []);

  const toggleItem = (globalIdx: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(globalIdx)) next.delete(globalIdx);
      else next.add(globalIdx);
      return next;
    });
  };

  // Build a unique display label for items that share a name
  const itemLabel = (item: FlatItem): string => {
    const dupes = flatItems.filter((i) => i.name === item.name);
    if (dupes.length <= 1) return item.name;
    const parts = [item.name];
    if (item.price != null) parts.push(`${Number(item.price)} kr`);
    else if (item.description) parts.push(item.description.slice(0, 30));
    return parts.join(" — ");
  };

  const handleSubmit = async () => {
    if (!name.trim() || selected.size === 0 || !id) return;
    setSubmitting(true);
    try {
      localStorage.setItem("lunch_name", name.trim());
      const selectedLabels = Array.from(selected).map((idx) => itemLabel(flatItems[idx]));
      await submitOrder(id, name.trim(), selectedLabels);
      setSubmitted(true);
    } catch {
      setError("Failed to submit order");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.topBar}>
        <Food24Regular style={{ color: "white" }} />
        <span className={styles.topBarText}>
          {session.title ?? session.restaurants?.map((r) => r.restaurant_name).join(" & ")}
          {session.description && ` — ${session.description}`}
        </span>
      </div>
      <div className={styles.content}>
        {submitted && (
          <div className={styles.successBanner}>
            <Text weight="semibold" style={{ color: "#190878" }}>
              Your order has been submitted! You can change it by submitting again.
            </Text>
          </div>
        )}

        <Card className={styles.card}>
          <Text size={500} weight="semibold">
            What would you like to order?
          </Text>

          <div className={styles.nameRow} style={{ marginTop: 16 }}>
            <div style={{ flex: 1 }}>
              <Text size={300} weight="semibold" style={{ display: "block", marginBottom: 4 }}>
                Your name
              </Text>
              <Input
                placeholder="Enter your name"
                value={name}
                onChange={(_, d) => setName(d.value)}
                style={{ width: "100%" }}
              />
            </div>
          </div>

          {session.restaurants.map((restaurant, ri) => {
            const color = getColor(restaurant.restaurant_name, ri);
            // Build grouped view for this restaurant, using globalIdx offsets
            const baseIdx = session.restaurants.slice(0, ri).reduce((s, r) => s + r.items.length, 0);

            const grouped = CATEGORY_ORDER
              .map((cat) => {
                const catItems = restaurant.items
                  .map((item, ii) => ({ ...item, globalIdx: baseIdx + ii }))
                  .filter((item) => item.category === cat);
                const hasSubcategories = cat === "main" && catItems.some((i) => i.subcategory);
                const subgroups: { label: string | null; items: typeof catItems }[] = hasSubcategories
                  ? Array.from(
                      catItems.reduce((map, item) => {
                        const k = item.subcategory ?? "";
                        if (!map.has(k)) map.set(k, []);
                        map.get(k)!.push(item);
                        return map;
                      }, new Map<string, typeof catItems>())
                    ).map(([label, items]) => ({ label: label || null, items }))
                  : [{ label: null, items: catItems }];
                return { category: cat, items: catItems, subgroups };
              })
              .filter((g) => g.items.length > 0);

            return (
              <div key={ri} className={styles.restaurantSection} style={{ marginTop: 16 }}>
                <div
                  className={styles.restaurantHeader}
                  style={{ backgroundColor: color.header }}
                >
                  <Text size={400} weight="semibold" style={{ color: "white" }}>
                    {restaurant.restaurant_name}
                  </Text>
                </div>
                <div className={styles.restaurantBody} style={{ backgroundColor: color.bg }}>
                  {grouped.map((group) => (
                    <div key={group.category}>
                      <Text className={styles.category} size={300} weight="semibold">
                        <Badge
                          appearance="filled"
                          style={{ backgroundColor: color.header, color: "white", marginRight: 8 }}
                        >
                          {group.category}
                        </Badge>
                      </Text>
                      {group.subgroups.map((sub, si) => (
                        <div key={sub.label ?? si}>
                          {sub.label && (
                            <Text
                              size={200}
                              weight="semibold"
                              style={{
                                display: "block",
                                marginTop: 10,
                                marginBottom: 2,
                                color: color.header,
                                textTransform: "uppercase",
                                letterSpacing: "0.04em",
                              }}
                            >
                              {sub.label}
                            </Text>
                          )}
                          {sub.items.map((item) => (
                            <div className={styles.item} key={item.globalIdx}>
                              <div className={styles.itemLeft}>
                                <Checkbox
                                  checked={selected.has(item.globalIdx)}
                                  onChange={() => toggleItem(item.globalIdx)}
                                />
                                <div>
                                  <Text weight="semibold">{item.name}</Text>
                                  {item.description && (
                                    <div>
                                      <Text size={200} style={{ color: "#616161" }}>
                                        {item.description}
                                      </Text>
                                    </div>
                                  )}
                                </div>
                              </div>
                              {item.price != null && (
                                <Text className={styles.price}>
                                  {Number(item.price)} kr
                                </Text>
                              )}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          <div className={styles.actions}>
            <Button
              appearance="primary"
              icon={<Send24Regular />}
              onClick={handleSubmit}
              disabled={submitting || !name.trim() || selected.size === 0}
              style={{ backgroundColor: "#190878", border: "none" }}
            >
              {submitting ? "Submitting…" : "Submit Order"}
            </Button>
            <Text size={200} style={{ color: "#616161" }}>
              {selected.size} item{selected.size !== 1 ? "s" : ""} selected
            </Text>
          </div>
        </Card>

        <Divider />

        <OrderList session={session} />

        <div style={{ display: "flex", justifyContent: "center", padding: "8px 0 24px" }}>
          <CsvButton sessionId={session.id} />
        </div>
      </div>
    </div>
  );
}
