export default function ReportViewer({ reports }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Rapports IA ({reports.length})</h2>
      {reports.length === 0 ? (
        <div style={styles.empty}>Aucun rapport genere pour le moment</div>
      ) : (
        <div style={styles.list}>
          {reports.map(function (report, idx) {
            var url = "http://localhost:5001" + report.download_url;
            return (
              <a key={idx} href={url} target="_blank" rel="noreferrer" style={styles.item}>
                {"[PDF] " + report.filename}
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { color: "#e5e7eb", background: "#1f2937", borderRadius: "8px", padding: "1rem", border: "1px solid #374151" },
  title: { fontSize: "1.25rem", marginBottom: "1rem" },
  empty: { color: "#9ca3af", fontSize: "0.85rem" },
  list: { display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "300px", overflowY: "auto" },
  item: { color: "#93c5fd", fontSize: "0.85rem", textDecoration: "none", padding: "0.4rem", borderRadius: "4px", background: "#111827" },
};
