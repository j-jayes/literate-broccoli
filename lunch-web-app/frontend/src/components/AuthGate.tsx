import { useState, type ReactNode } from "react";
import {
  Card,
  CardHeader,
  Input,
  Button,
  Spinner,
  Text,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { LockClosed24Regular } from "@fluentui/react-icons";
import { useAuth } from "../hooks/useAuth";

const useStyles = makeStyles({
  container: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    backgroundColor: "#ebebeb",
  },
  card: {
    width: "380px",
    padding: "32px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    marginTop: "16px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  brand: {
    display: "flex",
    flexDirection: "column",
  },
  error: {
    color: tokens.colorPaletteRedForeground1,
    fontSize: "13px",
  },
});

interface Props {
  children: ReactNode;
}

export default function AuthGate({ children }: Props) {
  const styles = useStyles();
  const { authenticated, login } = useAuth();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (authenticated === null) {
    return (
      <div className={styles.container}>
        <Spinner label="Checking authentication..." />
      </div>
    );
  }

  if (authenticated) {
    return <>{children}</>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(password);
    } catch {
      setError("Incorrect password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Card className={styles.card}>
        <div className={styles.header}>
          <LockClosed24Regular />
          <div className={styles.brand}>
            <Text size={500} weight="semibold">
              Lunch Order
            </Text>
            <Text size={200} style={{ color: "#616161" }}>
              Nexer Insight Demo
            </Text>
          </div>
        </div>
        <form className={styles.form} onSubmit={handleSubmit}>
          <Input
            placeholder="Enter password"
            type="password"
            value={password}
            onChange={(_, d) => setPassword(d.value)}
            autoFocus
          />
          {error && <Text className={styles.error}>{error}</Text>}
          <Button appearance="primary" type="submit" disabled={loading}>
            {loading ? <Spinner size="tiny" /> : "Sign In"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
