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
import type { LunchSession, MenuItem } from "../types";
import OrderList from "./OrderList";
import CsvButton from "./CsvButton";

const useStyles = makeStyles({
  page: {
    minHeight: "100vh",
    backgroundColor: "#ebebeb",
  },
  topBar: {
    backgroundColor: "#6264a7",
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
    backgroundColor: "#e8f5e9",
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

  const toggleItem = (idx: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  // Build unique display labels for items with duplicate names
  const itemLabel = (item: MenuItem, idx: number): string => {
    const dupes = session.items.filter((i) => i.name === item.name);
    if (dupes.length <= 1) return item.name;
    // Disambiguate with price or description
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
      // Send unique labels so the backend can distinguish duplicate names
      const selectedLabels = Array.from(selected).map((idx) =>
        itemLabel(session.items[idx], idx)
      );
      await submitOrder(id, name.trim(), selectedLabels);
      setSubmitted(true);
    } catch {
      setError("Failed to submit order");
    } finally {
      setSubmitting(false);
    }
  };

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    items: session.items
      .map((item, idx) => ({ ...item, idx }))
      .filter((item) => item.category === cat),
  })).filter((g) => g.items.length > 0);

  return (
    <div className={styles.page}>
      <div className={styles.topBar}>
        <Food24Regular style={{ color: "white" }} />
        <span className={styles.topBarText}>
          Lunch Order: {session.restaurant_name}
          {session.description && ` — ${session.description}`}
        </span>
      </div>
      <div className={styles.content}>
        {submitted && (
          <div className={styles.successBanner}>
            <Text weight="semibold" style={{ color: "#2e7d32" }}>
              Your order has been submitted! You can change it by submitting
              again.
            </Text>
          </div>
        )}

        <Card className={styles.card}>
          <Text size={500} weight="semibold">
            What would you like to order?
          </Text>

          <div className={styles.nameRow} style={{ marginTop: 16 }}>
            <div style={{ flex: 1 }}>
              <Text
                size={300}
                weight="semibold"
                style={{ display: "block", marginBottom: 4 }}
              >
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

          {grouped.map((group) => (
            <div key={group.category}>
              <Text className={styles.category} size={300} weight="semibold">
                <Badge
                  appearance="filled"
                  color="brand"
                  style={{ marginRight: 8 }}
                >
                  {group.category}
                </Badge>
              </Text>
              {group.items.map((item) => (
                <div className={styles.item} key={item.idx}>
                  <div className={styles.itemLeft}>
                    <Checkbox
                      checked={selected.has(item.idx)}
                      onChange={() => toggleItem(item.idx)}
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

          <div className={styles.actions}>
            <Button
              appearance="primary"
              icon={<Send24Regular />}
              onClick={handleSubmit}
              disabled={submitting || !name.trim() || selected.size === 0}
            >
              {submitting ? "Submitting..." : "Submit Order"}
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
