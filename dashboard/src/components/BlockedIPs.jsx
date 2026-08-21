export default function BlockedIPs({ ips }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>IPs bloquées ({ips.length})</h2>
      {ips.length === 0 ? (
        <div style={styles.empty}>Aucune IP bloquée pour le moment</div>
      ) : (
        <div style={styles.list}>
          {ips.map((item, idx) => (
            <div key={idx} style={styles.chip}>
              {item.ip || JSON.stringify(item)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { color: "#e5e7eb", background: "#1f2937", borderRadius: "8px", padding: "1rem", border: "1px solid #374151" },
  title: { fontSize: "1.25rem", marginBottom: "1rem" },
  empty: { color: "#9ca3af", fontSize: "0.85rem" },
  list: { display: "flex", flexWrap: "wrap", gap: "0.5rem" },
  chip: { background: "#7f1d1d", color: "#fecaca", fontFamily: "monospace", fontSize: "0.8rem", padding: "0.3rem 0.6rem", borderRadius: "999px" },
};
