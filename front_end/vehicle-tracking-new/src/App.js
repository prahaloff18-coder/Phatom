import React, { useEffect, useState } from "react";

function App() {
  const BASE_URL = "http://10.78.6.185:8001"; // your backend IP

  const [summary, setSummary] = useState({});
  const [vehicles, setVehicles] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Fetch Summary
  const loadSummary = async () => {
    try {
      const res = await fetch(`${BASE_URL}/summary`);
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.log("Summary error:", err);
    }
  };

  // Fetch Vehicles
  const loadVehicles = async () => {
    try {
      const res = await fetch(`${BASE_URL}/vehicles`);
      const data = await res.json();
      setVehicles(data.data || []);
    } catch (err) {
      console.log("Vehicles error:", err);
    }
  };

  // Fetch Alerts
  const loadAlerts = async () => {
    try {
      const res = await fetch(`${BASE_URL}/alerts`);
      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      console.log("Alerts error:", err);
    }
  };

  // Load only once (NO auto refresh to avoid errors)
  useEffect(() => {
    loadSummary();
    loadVehicles();
    loadAlerts();
  }, []);

  // Remove duplicate vehicles (based on vehicle_id)
  const uniqueVehicles = Array.from(
    new Map(vehicles.map((v) => [v[1], v])).values()
  );

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>🚗 Vehicle Dashboard</h1>

      {/* Refresh Button */}
      <button
        onClick={() => {
          loadSummary();
          loadVehicles();
          loadAlerts();
        }}
        style={{ padding: "8px 15px", marginBottom: "20px" }}
      >
        Refresh 🔄
      </button>

      {/* SUMMARY */}
      <h2>Summary</h2>
      <p><b>Total Vehicles:</b> {summary.total_vehicles || 0}</p>
      <p><b>Bikes:</b> {summary.by_type?.bike || 0}</p>
      <p><b>Cars:</b> {summary.by_type?.car || 0}</p>

      {/* VEHICLES */}
      <h2 style={{ marginTop: "30px" }}>Vehicles</h2>
      <table border="1" cellPadding="10" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Frame</th>
            <th>BBOX</th>
          </tr>
        </thead>
        <tbody>
          {uniqueVehicles.map((v, i) => (
            <tr key={i}>
              <td>{v[1]}</td>
              <td>{v[2]}</td>
              <td>{v[3]}</td>
              <td>{v[4]}, {v[5]}, {v[6]}, {v[7]}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ALERTS */}
      <h2 style={{ marginTop: "30px" }}>Alerts 🚨</h2>
      <table border="1" cellPadding="10" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Vehicle ID</th>
            <th>Type</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((a, i) => (
            <tr key={i} style={{ backgroundColor: "#ffe6e6", color: "red" }}>
              <td>{a.id}</td>
              <td>{a.vehicle_id}</td>
              <td>{a.type}</td>
              <td>{a.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;