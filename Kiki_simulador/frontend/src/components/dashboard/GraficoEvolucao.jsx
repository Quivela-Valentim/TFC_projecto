import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { formatarAOA, formatarData } from "../../utils/formatadores";

export default function GraficoEvolucao({ dados, chaveValor = "preco_fecho", altura = 260 }) {
  if (!dados || dados.length === 0) {
    return <div className="h-[260px] flex items-center justify-center text-sm text-marfim-400">Sem dados históricos suficientes para desenhar o gráfico.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <LineChart data={dados} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#16294F" vertical={false} />
        <XAxis dataKey="data" tickFormatter={formatarData} stroke="#93A5C9" fontSize={11} tickLine={false} axisLine={false} />
        <YAxis stroke="#93A5C9" fontSize={11} tickLine={false} axisLine={false} width={70} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
        <Tooltip
          contentStyle={{ background: "#0F1F3D", border: "1px solid #16294F", borderRadius: 12, fontSize: 12 }}
          labelStyle={{ color: "#93A5C9" }}
          labelFormatter={formatarData}
          formatter={(v) => [formatarAOA(v), "Preço"]}
        />
        <Line type="monotone" dataKey={chaveValor} stroke="#2B6CFF" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
