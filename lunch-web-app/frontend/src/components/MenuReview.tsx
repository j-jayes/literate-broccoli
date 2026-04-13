import { useState } from "react";
import {
  Card,
  Text,
  Button,
  Checkbox,
  Badge,
  Input,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import {
  Clipboard24Regular,
  CheckmarkCircle24Regular,
} from "@fluentui/react-icons";
import { createSession } from "../api";
import type { RestaurantMenu } from "../types";

// Nexer brand colors assigned per restaurant
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
  restaurantSection: {
    borderRadius: "10px",
    overflow: "hidden",
    marginBottom: "16px",
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  restaurantHeader: {
    padding: "12px 20px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  restaurantBody: {
    padding: "16px 20px",
  },
  category: {
    marginTop: "16px",
    marginBottom: "8px",
    textTransform: "capitalize",
  },
  item: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "8px 0",
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  itemLeft: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    flex: 1,
  },
  itemName: { fontWeight: 600 },
  itemDesc: { color: "#616161", fontSize: "12px" },
  price: { fontWeight: 600, whiteSpace: "nowrap" as const },
  sessionInfo: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    marginTop: "20px",
    padding: "16px",
    backgroundColor: "#f5f5f5",
    borderRadius: "8px",
  },
  actions: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginTop: "20px",
  },
  shareBox: {
    marginTop: "16px",
    padding: "16px",
    backgroundColor: "#D9E6F0",
    borderRadius: "8px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  urlRow: {
    display: "flex",
    gap: "8px",
    alignItems: "center",
  },
});

const CATEGORY_ORDER = ["main", "side", "drink", "dessert", "other"];

interface Props {
  restaurants: RestaurantMenu[];
}

// Stable key for an item: "restaurantIndex:itemIndex"
type ItemKey = string;

export default function MenuReview({ restaurants }: Props) {
  const styles = useStyles();

  // selected: set of "restaurantIdx:itemIdx" keys
  const [selected, setSelected] = useState<Set<ItemKey>>(() => {
    const all = new Set<ItemKey>();
    restaurants.forEach((r, ri) => r.items.forEach((_, ii) => all.add(`${ri}:${ii}`)));
    return all;
  });

  const [description, setDescription] = useState(() => {
    const today = new Date().toLocaleDateString("sv-SE");
    return `Lunch ${today}`;
  });
  const [sessionUrl, setSessionUrl] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [createError, setCreateError] = useState("");

  const toggle = (key: ItemKey) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const totalItems = restaurants.reduce((s, r) => s + r.items.length, 0);

  const handleCreate = async () => {
    setCreating(true);
    setCreateError("");
    try {
      // Build filtered restaurants keeping only selected items
      const filtered: RestaurantMenu[] = restaurants
        .map((r, ri) => ({
          restaurant_name: r.restaurant_name,
          items: r.items.filter((_, ii) => selected.has(`${ri}:${ii}`)),
        }))
        .filter((r) => r.items.length > 0);

      const session = await createSession(filtered, description.trim() || undefined);
      setSessionUrl(`${window.location.origin}/session/${session.id}`);
    } catch (err: any) {
      setCreateError(err.message || "Failed to create session");
    } finally {
      setCreating(false);
    }
  };

  const handleCopy = async () => {
    if (sessionUrl) {
      await navigator.clipboard.writeText(sessionUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <>
      <Card style={{ padding: "24px" }}>
        <Text size={500} weight="semibold">
          Review Menu
        </Text>
        <Text size={300} style={{ color: "#616161", marginTop: "4px" }}>
          {totalItems} items across {restaurants.length} restaurant{restaurants.length !== 1 ? "s" : ""}. Deselect any items you don't want in the poll.
        </Text>

        <div style={{ marginTop: "20px" }}>
          {restaurants.map((restaurant, ri) => {
            const color = getColor(restaurant.restaurant_name, ri);
            const grouped = CATEGORY_ORDER
              .map((cat) => {
                const catItems = restaurant.items
                  .map((item, ii) => ({ ...item, key: `${ri}:${ii}` }))
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

            const selectedCount = restaurant.items.filter((_, ii) => selected.has(`${ri}:${ii}`)).length;

            return (
              <div key={ri} className={styles.restaurantSection}>
                <div
                  className={styles.restaurantHeader}
                  style={{ backgroundColor: color.header }}
                >
                  <Text size={400} weight="semibold" style={{ color: "white" }}>
                    {restaurant.restaurant_name}
                  </Text>
                  <Text size={200} style={{ color: "rgba(255,255,255,0.8)" }}>
                    {selectedCount} / {restaurant.items.length} selected
                  </Text>
                </div>
                <div className={styles.restaurantBody} style={{ backgroundColor: color.bg }}>
                  {grouped.map((group) => (
                    <div key={group.category}>
                      <Text className={styles.category} size={300} weight="semibold">
                        <Badge
                          appearance="filled"
                          style={{
                            backgroundColor: color.header,
                            color: "white",
                            marginRight: 8,
                          }}
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
                            <div className={styles.item} key={item.key}>
                              <div className={styles.itemLeft}>
                                <Checkbox
                                  checked={selected.has(item.key)}
                                  onChange={() => toggle(item.key)}
                                />
                                <div>
                                  <Text className={styles.itemName}>{item.name}</Text>
                                  {item.description && (
                                    <div>
                                      <Text className={styles.itemDesc}>
                                        {item.description}
                                      </Text>
                                    </div>
                                  )}
                                </div>
                              </div>
                              {item.price != null && (
                                <Text className={styles.price}>{Number(item.price)} kr</Text>
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
        </div>

        {!sessionUrl && (
          <div className={styles.sessionInfo}>
            <Text size={300} weight="semibold">Poll Details</Text>
            <Input
              placeholder="e.g. Friday lunch, Team outing, etc."
              value={description}
              onChange={(_, d) => setDescription(d.value)}
            />
          </div>
        )}

        {createError && (
          <Text style={{ color: tokens.colorPaletteRedForeground1, marginTop: 8 }}>
            {createError}
          </Text>
        )}

        <div className={styles.actions}>
          <Button
            appearance="primary"
            onClick={handleCreate}
            disabled={creating || selected.size === 0 || !!sessionUrl}
            style={{ backgroundColor: "#190878", border: "none" }}
          >
            {creating ? "Creating…" : `Create Poll (${selected.size} items)`}
          </Button>
          <Text size={200} style={{ color: "#616161" }}>
            {selected.size} of {totalItems} selected
          </Text>
        </div>
      </Card>

      {sessionUrl && (
        <Card style={{ padding: "24px", marginTop: "16px" }}>
          <div className={styles.shareBox}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <CheckmarkCircle24Regular style={{ color: "#190878" }} />
              <Text size={400} weight="semibold" style={{ color: "#190878" }}>
                Poll created!
              </Text>
            </div>
            <Text size={300}>
              Share this link with your colleagues so they can choose their lunch:
            </Text>
            <div className={styles.urlRow}>
              <Input value={sessionUrl} readOnly style={{ flex: 1 }} />
              <Button
                appearance="primary"
                icon={<Clipboard24Regular />}
                onClick={handleCopy}
                style={{ backgroundColor: "#190878", border: "none" }}
              >
                {copied ? "Copied!" : "Copy"}
              </Button>
            </div>
          </div>
        </Card>
      )}
    </>
  );
}
