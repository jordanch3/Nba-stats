import { useEffect, useState } from "react";
import {
  CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

const API = "http://127.0.0.1:8000";

function useFetch(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setError(null);
    if (!url) return;
    let cancelled = false;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { data, error };
}

function StandingsTable({ rows, onSelect }) {
  return (
    <table>
      <thead>
        <tr><th>#</th><th>Team</th><th>W</th><th>L</th><th>Win %</th></tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={r.team_id} onClick={() => onSelect(r.team_id)} style={{ cursor: "pointer" }}>
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

function PlayerSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const url = query.trim().length >= 2 ? `${API}/players?q=${encodeURIComponent(query.trim())}` : null;
  const { data } = useFetch(url);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search players..."
      />
      {data && data.length === 0 && <p>No players found</p>}
      {data && (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {data.map((p) => (
            <li key={p.id}>
              <button onClick={() => onSelect(p.id)}>{p.name}</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function TeamPage({ teamId, onBack }) {
  const { data, error } = useFetch(`${API}/teams/${teamId}`);

  return (
    <section>
      <button onClick={onBack}>← Back</button>
      {error && <p>Could not load team: {error}</p>}
      {!data && !error && <p>Loading...</p>}
      {data && (
        <>
          <h2>{data.team}</h2>
          <p>Last 5: {data.last_5.join(" ") || "No games yet"}</p>
          <p>Home: {data.home.wins}-{data.home.losses}</p>
          <p>Away: {data.away.wins}-{data.away.losses}</p>
          <p>Avg scored: {data.avg_scored}</p>
          <p>Avg allowed: {data.avg_allowed}</p>
        </>
      )}
    </section>
  );
}

function PlayerPage({ playerId, onBack }) {
  const { data, error } = useFetch(`${API}/players/${playerId}`);

  return (
    <section>
      <button onClick={onBack}>← Back</button>
      {error && <p>Could not load player: {error}</p>}
      {!data && !error && <p>Loading...</p>}
      {data && (
        <>
          <h2>{data.name}</h2>
          <p>{data.games_played} games played</p>
          <p>
            {data.averages.pts} PTS · {data.averages.reb} REB · {data.averages.ast} AST ·{" "}
            {data.averages.min} MIN
          </p>
          <p>
            FG {(data.shooting.fg_pct * 100).toFixed(1)}% · 3P{" "}
            {(data.shooting.fg3_pct * 100).toFixed(1)}% · FT{" "}
            {(data.shooting.ft_pct * 100).toFixed(1)}%
          </p>
          <h3>Last {data.last_10.length} games</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[...data.last_10].reverse()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="pts" name="PTS" stroke="#aa3bff" />
              <Line type="monotone" dataKey="reb" name="REB" stroke="#2f9e44" />
              <Line type="monotone" dataKey="ast" name="AST" stroke="#e8590c" />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </section>
  );
}

export default function App() {
  const [conference, setConference] = useState("East");
  const [teamId, setTeamId] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const { data: rows, error } = useFetch(`${API}/standings?conference=${conference}`);

  if (teamId !== null) {
    return <main><TeamPage teamId={teamId} onBack={() => setTeamId(null)} /></main>;
  }
  if (playerId !== null) {
    return <main><PlayerPage playerId={playerId} onBack={() => setPlayerId(null)} /></main>;
  }

  return (
    <main>
      <h1>NBA Stats</h1>
      <PlayerSearch onSelect={setPlayerId} />
      <h2>Standings</h2>
      <div>
        {["East", "West"].map((c) => (
          <button key={c} onClick={() => setConference(c)} disabled={c === conference}>
            {c}
          </button>
        ))}
      </div>
      {error && <p>Could not load standings: {error}</p>}
      {rows && <StandingsTable rows={rows} onSelect={setTeamId} />}
    </main>
  );
}