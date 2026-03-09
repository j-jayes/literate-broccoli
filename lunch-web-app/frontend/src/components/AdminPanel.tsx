import { useState } from "react";
import {
  Card,
  Input,
  Button,
  Spinner,
  Text,
  makeStyles,
  tokens,
  Divider,
} from "@fluentui/react-components";
import {
  Search24Regular,
  Food24Regular,
  ArrowReset24Regular,
} from "@fluentui/react-icons";
import { scrapeMenu } from "../api";
import type { MenuItem } from "../types";
import MenuReview from "./MenuReview";

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
  },
  card: {
    padding: "24px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    marginTop: "16px",
  },
  inputGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    flex: 1,
  },
  label: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#424242",
  },
  loading: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "16px",
    padding: "40px 0",
  },
  error: {
    color: tokens.colorPaletteRedForeground1,
    marginTop: "8px",
  },
});

interface ScrapeResult {
  restaurantName: string;
  items: MenuItem[];
}

export default function AdminPanel() {
  const styles = useStyles();
  const [restaurantName, setRestaurantName] = useState("");
  const [menuUrl, setMenuUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Store scrape result separately so the restaurant name is locked
  const [result, setResult] = useState<ScrapeResult | null>(null);

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!restaurantName.trim()) return;
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const items = await scrapeMenu(
        restaurantName.trim(),
        menuUrl.trim() || undefined
      );
      // Lock the restaurant name at scrape time
      setResult({ restaurantName: restaurantName.trim(), items });
    } catch (err: any) {
      setError(err.message || "Failed to scrape menu");
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    setResult(null);
    setError("");
    setRestaurantName("");
    setMenuUrl("");
  };

  return (
    <div className={styles.page}>
      <div className={styles.topBar}>
        <Food24Regular style={{ color: "white" }} />
        <span className={styles.topBarText}>Lunch Order - Admin</span>
      </div>
      <div className={styles.content}>
        <Card className={styles.card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Text size={500} weight="semibold">
              Find Restaurant Menu
            </Text>
            {result && (
              <Button
                appearance="subtle"
                icon={<ArrowReset24Regular />}
                onClick={handleNewSearch}
              >
                New Search
              </Button>
            )}
          </div>
          <Text size={300} style={{ color: "#616161", marginTop: "4px" }}>
            Enter a restaurant name and the AI agent will find the website,
            navigate to the menu page, and extract all items automatically.
            We search for restaurants in Malmö by default.
          </Text>
          {!result && (
            <form className={styles.form} onSubmit={handleScrape}>
              <div className={styles.inputGroup}>
                <Text className={styles.label}>Restaurant Name</Text>
                <Input
                  placeholder="e.g. Pizzeria Napoli"
                  value={restaurantName}
                  onChange={(_, d) => setRestaurantName(d.value)}
                  disabled={loading}
                />
              </div>
              <div className={styles.inputGroup}>
                <Text className={styles.label}>
                  Website URL{" "}
                  <span style={{ fontWeight: 400, color: "#999" }}>
                    (optional — the AI agent will find it if left blank)
                  </span>
                </Text>
                <Input
                  placeholder="https://example.com/menu"
                  value={menuUrl}
                  onChange={(_, d) => setMenuUrl(d.value)}
                  disabled={loading}
                />
              </div>
              <Button
                appearance="primary"
                type="submit"
                disabled={loading || !restaurantName.trim()}
                icon={<Search24Regular />}
              >
                Find Menu
              </Button>
            </form>
          )}
          {error && <Text className={styles.error}>{error}</Text>}
        </Card>

        {loading && (
          <Card className={styles.card} style={{ marginTop: "16px" }}>
            <div className={styles.loading}>
              <Spinner size="large" />
              <Text size={400} weight="semibold">
                AI Agent is browsing the restaurant website...
              </Text>
              <Text size={300} style={{ color: "#616161" }}>
                This may take 15-30 seconds. The agent navigates the site,
                finds the menu page, and extracts all items.
              </Text>
            </div>
          </Card>
        )}

        {result && !loading && (
          <>
            <Divider style={{ margin: "24px 0" }} />
            <MenuReview
              restaurantName={result.restaurantName}
              items={result.items}
            />
          </>
        )}
      </div>
    </div>
  );
}
