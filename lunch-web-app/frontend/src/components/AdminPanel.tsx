import { useEffect, useState } from "react";
import {
  Card,
  Input,
  Button,
  Spinner,
  Text,
  Checkbox,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import {
  Search24Regular,
  Food24Regular,
  ArrowReset24Regular,
  Add24Regular,
  Dismiss24Regular,
} from "@fluentui/react-icons";
import { getCachedRestaurants, scrapeMenu } from "../api";
import type { RestaurantMenu } from "../types";
import MenuReview from "./MenuReview";

// Nexer brand colors for each cached restaurant slot
const RESTAURANT_COLORS: Record<string, { bg: string; header: string }> = {
  "Holy Greens": { bg: "#D9E6F0", header: "#190878" },
  "Dockside Burgers": { bg: "#FFE8DE", header: "#FF875A" },
};
const FALLBACK_COLORS = [
  { bg: "#F0E6FF", header: "#AA4BF5" },
  { bg: "#EDE0FF", header: "#5A1EA0" },
  { bg: "#F0F0F0", header: "#919191" },
];

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
    maxWidth: "800px",
    margin: "24px auto",
    padding: "0 16px",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  card: {
    padding: "24px",
  },
  sectionTitle: {
    marginBottom: "16px",
  },
  restaurantGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: "12px",
    marginTop: "12px",
  },
  restaurantCard: {
    borderRadius: "8px",
    padding: "16px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    cursor: "pointer",
    transition: "box-shadow 0.15s",
    border: "2px solid transparent",
  },
  restaurantCardSelected: {
    boxShadow: "0 0 0 2px #5A1EA0",
    border: "2px solid #5A1EA0",
  },
  restaurantLabel: {
    fontWeight: 600,
    fontSize: "14px",
  },
  customList: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    marginTop: "12px",
  },
  customItem: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 14px",
    backgroundColor: "#F0E6FF",
    borderRadius: "8px",
    border: "2px solid #AA4BF5",
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
  reviewButton: {
    marginTop: "4px",
  },
});

function getColor(name: string, index: number): { bg: string; header: string } {
  if (RESTAURANT_COLORS[name]) return RESTAURANT_COLORS[name];
  return FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

export default function AdminPanel() {
  const styles = useStyles();

  // Cached restaurants loaded from backend
  const [cachedRestaurants, setCachedRestaurants] = useState<RestaurantMenu[]>([]);
  const [selectedCached, setSelectedCached] = useState<Set<string>>(new Set());

  // Custom scraped restaurants added by the admin
  const [customRestaurants, setCustomRestaurants] = useState<RestaurantMenu[]>([]);

  // Scraper form state
  const [scraping, setScraping] = useState(false);
  const [scrapeError, setScrapeError] = useState("");
  const [restaurantName, setRestaurantName] = useState("");
  const [menuUrl, setMenuUrl] = useState("");
  const [showScraper, setShowScraper] = useState(false);

  // Show MenuReview once the admin clicks "Review & Create Poll"
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    getCachedRestaurants().then((restaurants) => {
      setCachedRestaurants(restaurants);
      // Pre-select all cached restaurants
      setSelectedCached(new Set(restaurants.map((r) => r.restaurant_name)));
    });
  }, []);

  const toggleCached = (name: string) => {
    setSelectedCached((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const handleScrape = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (!restaurantName.trim()) return;
    setScrapeError("");
    setScraping(true);
    try {
      const items = await scrapeMenu(restaurantName.trim(), menuUrl.trim() || undefined);
      setCustomRestaurants((prev) => [
        ...prev,
        { restaurant_name: restaurantName.trim(), items },
      ]);
      setRestaurantName("");
      setMenuUrl("");
      setShowScraper(false);
    } catch (err: any) {
      setScrapeError(err.message || "Failed to scrape menu");
    } finally {
      setScraping(false);
    }
  };

  const removeCustom = (name: string) => {
    setCustomRestaurants((prev) => prev.filter((r) => r.restaurant_name !== name));
  };

  // Assemble the final list in order: selected cached + custom scraped
  const selectedRestaurants: RestaurantMenu[] = [
    ...cachedRestaurants.filter((r) => selectedCached.has(r.restaurant_name)),
    ...customRestaurants,
  ];

  if (reviewing && selectedRestaurants.length > 0) {
    return (
      <div className={styles.page}>
        <div className={styles.topBar}>
          <Food24Regular style={{ color: "white" }} />
          <span className={styles.topBarText}>Lunch Order — Admin</span>
        </div>
        <div className={styles.content}>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Button
              appearance="subtle"
              icon={<ArrowReset24Regular />}
              onClick={() => setReviewing(false)}
            >
              Back to selection
            </Button>
          </div>
          <MenuReview restaurants={selectedRestaurants} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.topBar}>
        <Food24Regular style={{ color: "white" }} />
        <span className={styles.topBarText}>Lunch Order — Admin</span>
      </div>
      <div className={styles.content}>
        {/* Cached restaurant selection */}
        <Card className={styles.card}>
          <Text size={500} weight="semibold" className={styles.sectionTitle}>
            Today's Restaurants
          </Text>
          <Text size={300} style={{ color: "#616161" }}>
            Select which restaurants to include in today's lunch poll.
          </Text>

          <div className={styles.restaurantGrid}>
            {cachedRestaurants.map((r, i) => {
              const color = getColor(r.restaurant_name, i);
              const isSelected = selectedCached.has(r.restaurant_name);
              return (
                <div
                  key={r.restaurant_name}
                  className={`${styles.restaurantCard}${isSelected ? " " + styles.restaurantCardSelected : ""}`}
                  style={{ backgroundColor: color.bg }}
                  onClick={() => toggleCached(r.restaurant_name)}
                >
                  <Checkbox
                    checked={isSelected}
                    onChange={() => toggleCached(r.restaurant_name)}
                  />
                  <div>
                    <Text className={styles.restaurantLabel} style={{ color: color.header }}>
                      {r.restaurant_name}
                    </Text>
                    <Text size={200} style={{ color: "#616161" }}>
                      {r.items.length} items cached
                    </Text>
                  </div>
                </div>
              );
            })}

            {customRestaurants.map((r, i) => {
              const color = FALLBACK_COLORS[i % FALLBACK_COLORS.length];
              return (
                <div
                  key={r.restaurant_name}
                  className={styles.restaurantCard}
                  style={{ backgroundColor: color.bg, border: `2px solid ${color.header}` }}
                >
                  <div style={{ flex: 1 }}>
                    <Text className={styles.restaurantLabel} style={{ color: color.header }}>
                      {r.restaurant_name}
                    </Text>
                    <Text size={200} style={{ color: "#616161" }}>
                      {r.items.length} items scraped
                    </Text>
                  </div>
                  <Button
                    appearance="subtle"
                    icon={<Dismiss24Regular />}
                    size="small"
                    onClick={() => removeCustom(r.restaurant_name)}
                    title="Remove"
                  />
                </div>
              );
            })}
          </div>
        </Card>

        {/* Add another restaurant via scraper */}
        <Card className={styles.card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Text size={400} weight="semibold">
              Add Another Restaurant
            </Text>
            {!showScraper && (
              <Button
                appearance="primary"
                icon={<Add24Regular />}
                size="small"
                style={{ backgroundColor: "#AA4BF5", border: "none" }}
                onClick={() => setShowScraper(true)}
              >
                Add
              </Button>
            )}
          </div>
          <Text size={300} style={{ color: "#616161", marginTop: "4px" }}>
            The AI agent will find the restaurant website and extract the menu automatically.
          </Text>

          {showScraper && !scraping && (
            <form className={styles.form} onSubmit={handleScrape}>
              <div className={styles.inputGroup}>
                <Text className={styles.label}>Restaurant Name</Text>
                <Input
                  placeholder="e.g. Pizzeria Napoli Malmö"
                  value={restaurantName}
                  onChange={(_, d) => setRestaurantName(d.value)}
                  disabled={scraping}
                />
              </div>
              <div className={styles.inputGroup}>
                <Text className={styles.label}>
                  Website URL{" "}
                  <span style={{ fontWeight: 400, color: "#999" }}>(optional)</span>
                </Text>
                <Input
                  placeholder="https://example.com/menu"
                  value={menuUrl}
                  onChange={(_, d) => setMenuUrl(d.value)}
                  disabled={scraping}
                />
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <Button
                  appearance="primary"
                  type="submit"
                  disabled={!restaurantName.trim()}
                  icon={<Search24Regular />}
                  style={{ backgroundColor: "#5A1EA0", border: "none" }}
                >
                  Find Menu
                </Button>
                <Button
                  appearance="subtle"
                  onClick={() => { setShowScraper(false); setScrapeError(""); }}
                >
                  Cancel
                </Button>
              </div>
              {scrapeError && <Text className={styles.error}>{scrapeError}</Text>}
            </form>
          )}

          {scraping && (
            <div className={styles.loading}>
              <Spinner size="medium" />
              <Text size={300} weight="semibold">
                AI Agent is browsing the restaurant website…
              </Text>
              <Text size={200} style={{ color: "#616161" }}>
                This may take 15–30 seconds.
              </Text>
            </div>
          )}
        </Card>

        {/* Review & Create Poll */}
        <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: "16px" }}>
          <Text size={300} style={{ color: "#616161" }}>
            {selectedRestaurants.length === 0
              ? "Select at least one restaurant to continue"
              : `${selectedRestaurants.length} restaurant${selectedRestaurants.length !== 1 ? "s" : ""} selected`}
          </Text>
          <Button
            appearance="primary"
            size="large"
            disabled={selectedRestaurants.length === 0}
            onClick={() => setReviewing(true)}
            style={{ backgroundColor: "#190878", border: "none" }}
          >
            Review &amp; Create Poll
          </Button>
        </div>
      </div>
    </div>
  );
}
