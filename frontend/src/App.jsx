import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

function StandingsTable({ rows }) {
  return (
    <table>
      <thead>
        <tr><th>#</th><th>Team</th><th>W</th><th>L</th><th>Win %</th></tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={r.team_id}>
            <td>{i + 1}</td>
            <td>{r.team}</td>
            <td>{r.wins}</td>
            <td>{r.losses}</td>
            <td>{r.win_pct.toFixed(3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function App() {
  const [conference, setConference] = useState("East");
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    fetch(`${API}/standings?conference=${conference}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setRows)
      .catch((e) => setError(e.message));
  }, [conference]);

  return (
    <main>
      <h1>NBA Standings</h1>
      <div>
        {["East", "West"].map((c) => (
          <button key={c} onClick={() => setConference(c)} disabled={c === conference}>
            {c}
          </button>
        ))}
      </div>
      {error ? <p>Could not load standings: {error}</p> : <StandingsTable rows={rows} />}
    </main>
  );
}