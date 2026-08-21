import { useEffect, useState } from "react";
import AlertsList from "./components/AlertsList";
import TrafficChart from "./components/TrafficChart";
import BlockedIPs from "./components/BlockedIPs";
import ReportViewer from "./components/ReportViewer";
import { getAlerts, getBlockedIps, getTraffic, getReports } from "./services/api";
import "./App.css";

const POLL_INTERVAL_MS = 8000;

function App() {
  const [alerts, setAlerts] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [traffic, setTraffic] = useState([]);
  const [reports, setReports] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchAll = async function () {
    try {
      const results = await Promise.all([
        getAlerts(),
        getBlockedIps(),
        getTraffic(),
        getReports(),
      ]);
      setAlerts(results[0]);
      setBlockedIps(results[1]);
      setTraffic(results[2]);
      setReports(results[3]);
      setLastUpdate(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      setError("Impossible de contacter l'API (http://localhost:5001). Le serveur Flask tourne-t-il ?");
    }
  };

  useEffect(function () {
    fetchAll();
    const interval = setInterval(fetchAll, POLL_INTERVAL_MS);
    return function () {
      clearInterval(interval);
    };
  }, []);

  const highCount = alerts.filter(function (a) { return a.severity === "high"; }).length;
  const mediumCount = alerts.filter(function (a) { return a.severity === "medium"; }).length;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>SHIELD</div>
          <div>
            <h1 style={styles.h1}>AI Cyber Defender</h1>
            <div style={styles.subtitle}>Dashboard de surveillance en temps reel</div>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.liveIndicator}>
            <span style={styles.liveDot}></span>
            LIVE
          </div>
          {lastUpdate && <span style={styles.lastUpdate}>Mis a jour a {lastUpdate}</span>}
        </div>
      </header>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>{alerts.length}</div>
          <div style={styles.statLabel}>Alertes totales</div>
        </div>
        <div style={{ ...styles.statCard, borderColor: "#ef4444" }}>
          <div style={{ ...styles.statValue, color: "#ef4444" }}>{highCount}</div>
          <div style={styles.statLabel}>Severite haute</div>
        </div>
        <div style={{ ...styles.statCard, borderColor: "#f59e0b" }}>
          <div style={{ ...styles.statValue, color: "#f59e0b" }}>{mediumCount}</div>
          <div style={styles.statLabel}>Severite moyenne</div>
        </div>
        <div style={{ ...styles.statCard, borderColor: "#7f1d1d" }}>
          <div style={{ ...styles.statValue, color: "#fca5a5" }}>{blockedIps.length}</div>
          <div style={styles.statLabel}>IPs bloquees</div>
        </div>
      </div>

      <div style={styles.grid}>
        <div style={styles.col}>
          <AlertsList alerts={alerts} />
        </div>
        <div style={styles.col}>
          <TrafficChart traffic={traffic} />
          <BlockedIPs ips={blockedIps} />
          <ReportViewer reports={reports} />
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(180deg, #0b1120 0%, #111827 100%)",
    padding: "2rem",
    fontFamily: "system-ui, -apple-system, sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1.5rem",
    flexWrap: "wrap",
    gap: "1rem",
  },
  headerLeft: { display: "flex", alignItems: "center", gap: "1rem" },
  logo: {
    fontSize: "0.7rem",
    fontWeight: "bold",
    letterSpacing: "0.1em",
    color: "#60a5fa",
    border: "1px solid #3b82f6",
    borderRadius: "6px",
    padding: "0.4rem 0.6rem",
  },
  h1: { color: "#f9fafb", fontSize: "1.6rem", margin: 0 },
  subtitle: { color: "#9ca3af", fontSize: "0.8rem", marginTop: "0.15rem" },
  headerRight: { display: "flex", alignItems: "center", gap: "1rem" },
  liveIndicator: {
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
    fontSize: "0.75rem",
    fontWeight: "bold",
    color: "#4ade80",
    background: "#052e16",
    padding: "0.3rem 0.7rem",
    borderRadius: "999px",
    border: "1px solid #166534",
  },
  liveDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#4ade80",
    display: "inline-block",
    animation: "pulse 1.5s infinite",
  },
  lastUpdate: { color: "#6b7280", fontSize: "0.75rem" },
  error: {
    background: "#7f1d1d",
    color: "#fecaca",
    padding: "0.75rem",
    borderRadius: "8px",
    marginBottom: "1rem",
  },
  statsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
    gap: "1rem",
    marginBottom: "1.5rem",
  },
  statCard: {
    background: "#1f2937",
    border: "1px solid #374151",
    borderRadius: "10px",
    padding: "1rem",
    textAlign: "center",
  },
  statValue: { fontSize: "2rem", fontWeight: "bold", color: "#f9fafb" },
  statLabel: { fontSize: "0.75rem", color: "#9ca3af", marginTop: "0.25rem" },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "1.5rem",
  },
  col: { display: "flex", flexDirection: "column", gap: "1.5rem" },
};

export default App;
