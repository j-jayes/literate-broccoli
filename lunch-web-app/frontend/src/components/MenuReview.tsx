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
import type { MenuItem } from "../types";

const useStyles = makeStyles({
  card: { padding: "24px" },
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
    backgroundColor: "#e8f5e9",
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
  restaurantName: string;
  items: MenuItem[];
}

export default function MenuReview({ restaurantName, items }: Props) {
  const styles = useStyles();
  const [selected, setSelected] = useState<Set<number>>(
    () => new Set(items.map((_, i) => i))
  );
  const [description, setDescription] = useState(() => {
    const today = new Date().toLocaleDateString("sv-SE");
    return `Lunch ${today}`;
  });
  const [sessionUrl, setSessionUrl] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [createError, setCreateError] = useState("");

  const toggle = (idx: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    items: items
      .map((item, idx) => ({ ...item, idx }))
      .filter((item) => item.category === cat),
  })).filter((g) => g.items.length > 0);

  const handleCreate = async () => {
    setCreating(true);
    setCreateError("");
    try {
      const selectedItems = items.filter((_, i) => selected.has(i));
      const session = await createSession(
        restaurantName,
        selectedItems,
        description.trim() || undefined
      );
      const url = `${window.location.origin}/session/${session.id}`;
      setSessionUrl(url);
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
      <Card className={styles.card}>
        <Text size={500} weight="semibold">
          Menu: {restaurantName}
        </Text>
        <Text size={300} style={{ color: "#616161" }}>
          {items.length} items found. Deselect any items you don't want in the
          poll.
        </Text>

        {grouped.map((group) => (
          <div key={group.category}>
            <Text className={styles.category} size={400} weight="semibold">
              <Badge appearance="filled" color="brand" style={{ marginRight: 8 }}>
                {group.category}
              </Badge>
            </Text>
            {group.items.map((item) => (
              <div className={styles.item} key={item.idx}>
                <div className={styles.itemLeft}>
                  <Checkbox
                    checked={selected.has(item.idx)}
                    onChange={() => toggle(item.idx)}
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

        {!sessionUrl && (
          <div className={styles.sessionInfo}>
            <Text size={300} weight="semibold">
              Poll Details
            </Text>
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
          >
            {creating ? "Creating..." : `Create Poll (${selected.size} items)`}
          </Button>
          <Text size={200} style={{ color: "#616161" }}>
            {selected.size} of {items.length} selected
          </Text>
        </div>
      </Card>

      {sessionUrl && (
        <Card className={styles.card} style={{ marginTop: "16px" }}>
          <div className={styles.shareBox}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <CheckmarkCircle24Regular style={{ color: "#2e7d32" }} />
              <Text size={400} weight="semibold" style={{ color: "#2e7d32" }}>
                Poll created!
              </Text>
            </div>
            <Text size={300}>
              Share this link with your colleagues so they can choose their
              lunch:
            </Text>
            <div className={styles.urlRow}>
              <Input
                value={sessionUrl}
                readOnly
                style={{ flex: 1 }}
              />
              <Button
                appearance="primary"
                icon={<Clipboard24Regular />}
                onClick={handleCopy}
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
