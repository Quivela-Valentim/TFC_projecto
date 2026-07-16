import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

export default function GraficoComparativo({ nominalPct, realPct, altura = 220 }) {
  const dados = [
    { nome: "Rentabilidade Nominal", valor: Number(nominalPct) },
    { nome: "Rentabilidade Real", valor: Number(realPct) },
  ];

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <BarChart data={dados} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#16294F" vertical={false} />
        <XAxis dataKey="nome" stroke="#93A5C9" fontSize={12} tickLine={false} axisLine={false} />
        <YAxis stroke="#93A5C9" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
        <Tooltip
          contentStyle={{ background: "#0F1F3D", border: "1px solid #16294F", borderRadius: 12, fontSize: 12 }}
          labelStyle={{ color: "#93A5C9" }}
          formatter={(v) => [`${Number(v).toFixed(2)}%`, "Rentabilidade"]}
        />
        <Bar dataKey="valor" radius={[8, 8, 0, 0]} maxBarSize={72}>
          {dados.map((d, i) => (
            <Cell key={i} fill={d.valor >= 0 ? "#22C55E" : "#EF4444"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
