import {
  Card,
  Text,
  Badge,
  Divider,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { People24Regular } from "@fluentui/react-icons";
import type { LunchSession } from "../types";

const useStyles = makeStyles({
  card: { padding: "24px" },
  person: {
    display: "flex",
    justifyContent: "space-between",
    padding: "8px 0",
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  personName: { fontWeight: 600 },
  combined: { marginTop: "12px" },
  combinedItem: {
    display: "flex",
    justifyContent: "space-between",
    padding: "4px 0",
  },
});

interface Props {
  session: LunchSession;
}

export default function OrderList({ session }: Props) {
  const styles = useStyles();
  const orders = Object.values(session.orders);

  // Aggregate counts
  const counts: Record<string, number> = {};
  for (const order of orders) {
    for (const item of order.items) {
      counts[item] = (counts[item] || 0) + 1;
    }
  }

  // Price lookup across all restaurants
  const priceMap: Record<string, number | null> = {};
  for (const restaurant of session.restaurants) {
    for (const item of restaurant.items) {
      priceMap[item.name] = item.price;
    }
  }

  return (
    <Card className={styles.card}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <People24Regular />
        <Text size={400} weight="semibold">
          Orders
        </Text>
        <Badge appearance="filled" color="brand">
          {orders.length} {orders.length === 1 ? "person" : "people"}
        </Badge>
      </div>

      {orders.length === 0 ? (
        <Text
          size={300}
          style={{ color: "#616161", marginTop: 12, display: "block" }}
        >
          No orders yet. Share the link and wait for colleagues to submit.
        </Text>
      ) : (
        <>
          {orders.map((order) => (
            <div className={styles.person} key={order.name}>
              <Text className={styles.personName}>{order.name}</Text>
              <Text size={300}>{order.items.join(", ")}</Text>
            </div>
          ))}

          <Divider style={{ margin: "16px 0 8px" }} />
          <Text size={400} weight="semibold">
            Combined Order
          </Text>
          <div className={styles.combined}>
            {Object.entries(counts)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([item, count]) => (
                <div className={styles.combinedItem} key={item}>
                  <Text>
                    {item} x{count}
                  </Text>
                  {priceMap[item] != null && (
                    <Text style={{ color: "#616161" }}>
                      {Number(priceMap[item]) * count} kr
                    </Text>
                  )}
                </div>
              ))}
          </div>
        </>
      )}
    </Card>
  );
}
