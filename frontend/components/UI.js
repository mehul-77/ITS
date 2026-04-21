"use client";

export function MetricCard({ label, value, sub, accent = "var(--accent2)" }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid var(--border)",
        borderRadius: 18,
        padding: "16px 18px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: "var(--muted)",
        }}
      >
        {label}
      </span>
      <span style={{ fontSize: 28, fontWeight: 700, color: accent, lineHeight: 1 }}>
        {value}
      </span>
      {sub ? <span style={{ color: "var(--muted)", fontSize: 12 }}>{sub}</span> : null}
    </div>
  );
}

export function Spinner({ size = 34, label = "Loading..." }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, padding: 28 }}>
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          border: "3px solid rgba(255,255,255,0.1)",
          borderTop: "3px solid var(--accent)",
          animation: "spin 0.9s linear infinite",
        }}
      />
      <span style={{ color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>{label}</span>
    </div>
  );
}

export function Btn({ children, onClick, disabled, loading, variant = "primary", style = {} }) {
  const variants = {
    primary: {
      background: "linear-gradient(135deg, var(--accent), #fb923c)",
      color: "#1c1202",
      border: "none",
    },
    secondary: {
      background: "linear-gradient(135deg, var(--accent2), #22c55e)",
      color: "#032319",
      border: "none",
    },
    ghost: {
      background: "rgba(255,255,255,0.03)",
      color: "var(--text)",
      border: "1px solid var(--border)",
    },
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        padding: "11px 16px",
        borderRadius: 14,
        fontWeight: 700,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        boxShadow: variant === "ghost" ? "none" : "var(--shadow)",
        ...variants[variant],
        ...style,
      }}
    >
      {loading ? (
        <span
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            border: "2px solid rgba(0,0,0,0.12)",
            borderTop: "2px solid currentColor",
            animation: "spin 0.9s linear infinite",
          }}
        />
      ) : null}
      {children}
    </button>
  );
}

export function SectionLabel({ children }) {
  return (
    <div
      style={{
        marginBottom: 12,
        color: "var(--muted)",
        fontFamily: "var(--font-mono)",
        fontSize: 11,
        letterSpacing: "0.16em",
        textTransform: "uppercase",
      }}
    >
      {children}
    </div>
  );
}

export function ErrorBox({ message }) {
  if (!message) return null;
  return (
    <div
      style={{
        background: "rgba(255, 107, 107, 0.1)",
        border: "1px solid rgba(255, 107, 107, 0.28)",
        borderRadius: 14,
        padding: "12px 14px",
        color: "var(--danger)",
        fontSize: 13,
      }}
    >
      {message}
    </div>
  );
}

export function ReadinessBadge({ its }) {
  if (!its) return null;
  const colorMap = {
    High: "var(--accent2)",
    Medium: "var(--warn)",
    Low: "var(--danger)",
  };

  const color = colorMap[its.label] || "var(--text)";

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)",
        border: `1px solid ${color}55`,
        borderRadius: 16,
        padding: "14px 16px",
      }}
    >
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color, marginBottom: 6 }}>
        {its.label} readiness
      </div>
      <div style={{ color: "var(--text)", fontSize: 13, lineHeight: 1.6 }}>{its.desc}</div>
    </div>
  );
}

export function TypeBar({ item }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "110px 1fr 56px", gap: 10, alignItems: "center", marginBottom: 8 }}>
      <div style={{ color: "var(--text)", fontSize: 12 }}>{item.label}</div>
      <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: 999, height: 8, overflow: "hidden" }}>
        <div style={{ width: `${item.percent}%`, height: "100%", background: item.color, borderRadius: 999 }} />
      </div>
      <div style={{ color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 11, textAlign: "right" }}>
        {item.length_km} km
      </div>
    </div>
  );
}
