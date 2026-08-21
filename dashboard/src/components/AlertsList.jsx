const SEVERITY_COLORS = {
  high: "#ef4444",
  medium: "#f59e0b",
  low: "#3b82f6",
  unknown: "#6b7280",
};

export default function AlertsList({ alerts }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Alertes ({alerts.length})</h2>
      <div style={styles.list}>
        {alerts.map((alert, idx) => (
          <div key={idx} style={styles.card}>
            <div style={styles.cardHeader}>
              <span
                style={{
                  ...styles.badge,
                  backgroundColor: SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS.unknown,
                }}
              >
                {alert.severity.toUpperCase()}
              </span>
              <span style={styles.type}>{alert.type}</span>
              {alert.blocked && <span style={styles.blockedBadge}>IP BLOQUÉE</span>}
            </div>
            <div style={styles.ip}>{alert.ip}</div>
            <div style={styles.timestamp}>{alert.last_seen}</div>
            <div style={styles.actions}>
              Actions : {alert.actions.join(", ") || "aucune"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: { color: "#e5e7eb" },
  title: { fontSize: "1.25rem", marginBottom: "1rem" },
  list: { display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "500px", overflowY: "auto" },
  card: { background: "#1f2937", borderRadius: "8px", padding: "1rem", border: "1px solid #374151" },
  cardHeader: { display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" },
  badge: { fontSize: "0.7rem", fontWeight: "bold", padding: "0.2rem 0.5rem", borderRadius: "4px", color: "#fff" },
  type: { fontWeight: "bold", fontSize: "0.9rem" },
  blockedBadge: { fontSize: "0.7rem", background: "#7f1d1d", padding: "0.2rem 0.5rem", borderRadius: "4px" },
  ip: { fontFamily: "monospace", fontSize: "0.9rem", color: "#93c5fd" },
  timestamp: { fontSize: "0.75rem", color: "#9ca3af" },
  actions: { fontSize: "0.75rem", color: "#9ca3af", marginTop: "0.25rem" },
};
