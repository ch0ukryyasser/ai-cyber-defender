import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function TrafficChart({ traffic }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Trafic (requêtes/minute)</h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={traffic}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#9ca3af" }} />
          <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} />
          <Tooltip
            contentStyle={{ background: "#1f2937", border: "1px solid #374151", color: "#e5e7eb" }}
          />
          <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

const styles = {
  container: { color: "#e5e7eb", background: "#1f2937", borderRadius: "8px", padding: "1rem", border: "1px solid #374151" },
  title: { fontSize: "1.25rem", marginBottom: "1rem" },
};
