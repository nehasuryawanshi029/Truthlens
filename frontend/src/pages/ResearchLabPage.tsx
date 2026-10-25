import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  ScatterChart as ScatterIcon,
  Layers,
  Cpu,
  BarChart3,
  Scale,
  Info,
  CheckCircle2,
  Table as TableIcon
} from 'lucide-react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { fetchResearchLabData } from '../services/api';
import { ResearchLabData } from '../types';

export const ResearchLabPage: React.FC = () => {
  const [data, setData] = useState<ResearchLabData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResearchLabData()
      .then(setData)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'flooding':
        return '#0284C7';
      case 'cyclone':
        return '#7C3AED';
      case 'earthquake':
        return '#EA580C';
      case 'protest':
        return '#DC2626';
      case 'local_incident':
        return '#65A30D';
      default:
        return '#1B3B2B';
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const pt = payload[0].payload;
      return (
        <div className="bg-[#FFFFFF] p-3 rounded-md border border-[#D9D3C7] shadow-lg text-xs max-w-xs space-y-1">
          <div className="font-bold text-[#1A1E1C]">{pt.title}</div>
          <div className="text-[11px] text-[#737E79]">Category: <span className="capitalize font-medium text-[#1B3B2B]">{pt.category}</span></div>
          <div className="text-[11px] text-[#737E79]">Source: {pt.publisher}</div>
          <div className="font-mono text-[10px] text-[#5C6661]">Coord: ({pt.x}, {pt.y})</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      <div className="pb-4 border-b border-[#E6E1D8]">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-[#EAF2ED] text-[#1B3B2B] text-xs font-semibold uppercase tracking-wider mb-2 border border-[#C5DDD0]">
          <FlaskConical className="w-3.5 h-3.5" />
          <span>Academic Evaluation Environment</span>
        </div>
        <h1 className="font-editorial text-3xl font-bold text-[#1A1E1C]">
          Research Lab & Methodology Cards
        </h1>
        <p className="text-sm text-[#4A5450] mt-1 max-w-3xl">
          Inspect multimodal feature projections, model architectures, and empirical evaluation metrics on benchmark visual misinformation datasets.
        </p>
      </div>

      {loading || !data ? (
        <div className="p-12 text-center text-xs text-[#737E79]">
          <div className="w-5 h-5 border-2 border-[#1B3B2B]/30 border-t-[#1B3B2B] rounded-full animate-spin mx-auto mb-2" />
          <span>Computing dimensionality reduction vectors...</span>
        </div>
      ) : (
        <>
          {/* Section 1: 2D PCA Dimensionality Reduction Projection */}
          <section className="editorial-card p-6 sm:p-8 space-y-6 bg-[#FFFFFF]">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#F4F1EA]">
              <div>
                <h2 className="font-editorial text-xl font-bold text-[#1A1E1C] flex items-center gap-2">
                  <ScatterIcon className="w-5 h-5 text-[#1B3B2B]" />
                  <span>Multimodal Feature Space (2D PCA Projection)</span>
                </h2>
                <p className="text-xs text-[#5C6661] mt-1">
                  Linear projection of TF-IDF n-gram and perceptual hash vectors across the reference corpus.
                </p>
              </div>
              <div className="text-[11px] font-mono text-[#737E79] bg-[#FBF9F5] px-3 py-1 rounded border border-[#E6E1D8]">
                Explained Variance: PC1 ({Math.round(data.pca_variance_ratio[0] * 100)}%), PC2 ({Math.round(data.pca_variance_ratio[1] * 100)}%)
              </div>
            </div>

            {/* Projection Chart */}
            <div className="h-80 w-full bg-[#FBF9F5] rounded-md border border-[#E6E1D8] p-4 relative">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <XAxis type="number" dataKey="x" name="Principal Component 1" domain={[-100, 100]} tick={{ fontSize: 10 }} />
                  <YAxis type="number" dataKey="y" name="Principal Component 2" domain={[-100, 100]} tick={{ fontSize: 10 }} />
                  <ZAxis range={[70, 70]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Scatter name="Corpus Elements" data={data.projection_points}>
                    {data.projection_points.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getCategoryColor(entry.category)} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            {/* Projection Legend & Epistemic Disclaimer */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 text-xs">
              <div className="flex flex-wrap items-center gap-4">
                <span className="text-[11px] font-semibold text-[#737E79] uppercase">Clusters:</span>
                {[
                  { cat: 'Flooding', color: '#0284C7' },
                  { cat: 'Cyclone', color: '#7C3AED' },
                  { cat: 'Earthquake', color: '#EA580C' },
                  { cat: 'Protest', color: '#DC2626' },
                  { cat: 'Local Incident', color: '#65A30D' },
                ].map((c) => (
                  <div key={c.cat} className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.color }} />
                    <span className="text-[#2C332F]">{c.cat}</span>
                  </div>
                ))}
              </div>

              <div className="text-[11px] text-[#737E79] italic flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-[#1B3B2B]" />
                <span>Note: This 2D visualization is a projection; semantic distance in high-dimensional space may differ.</span>
              </div>
            </div>
          </section>

          {/* Section 2: Empirical Evaluation Metrics */}
          <section className="editorial-card p-6 sm:p-8 space-y-6 bg-[#FFFFFF]">
            <div className="pb-4 border-b border-[#F4F1EA]">
              <h2 className="font-editorial text-xl font-bold text-[#1A1E1C] flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-[#1B3B2B]" />
                <span>Benchmark Evaluation Metrics (VERITE Alignment)</span>
              </h2>
              <p className="text-xs text-[#5C6661] mt-1">
                Empirical evaluation across {data.evaluation_metrics.sample_size} documented benchmark cases.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { label: 'Precision @ 1', val: data.evaluation_metrics.metrics.retrieval_precision_at_1 },
                { label: 'Recall @ 5', val: data.evaluation_metrics.metrics.retrieval_recall_at_5 },
                { label: 'Mean Reciprocal Rank', val: data.evaluation_metrics.metrics.mean_reciprocal_rank_mrr },
                { label: 'Claim Verif. F1', val: data.evaluation_metrics.metrics.claim_verification_f1 },
                { label: 'Abstention Rate', val: data.evaluation_metrics.metrics.abstention_rate_on_insufficient },
                { label: 'Synthetic FP Rate', val: data.evaluation_metrics.metrics.false_positive_rate_on_synthetic },
              ].map((m, idx) => (
                <div key={idx} className="p-4 bg-[#FBF9F5] rounded border border-[#E6E1D8]">
                  <span className="text-[10px] uppercase tracking-wider text-[#737E79] block mb-1">
                    {m.label}
                  </span>
                  <span className="font-mono text-xl font-bold text-[#1B3B2B]">
                    {(m.val * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>

            {/* Confusion Matrix Table */}
            <div className="pt-2">
              <h4 className="font-editorial text-sm font-bold text-[#1A1E1C] mb-3 flex items-center gap-1.5">
                <TableIcon className="w-4 h-4 text-[#1B3B2B]" />
                <span>Epistemic State Confusion Matrix</span>
              </h4>

              <div className="overflow-x-auto">
                <table className="w-full text-xs border border-[#E6E1D8] text-center">
                  <thead className="bg-[#1B3B2B] text-[#FBF9F5]">
                    <tr>
                      <th className="p-2.5 text-left font-semibold">Predicted \ Actual</th>
                      {data.evaluation_metrics.confusion_matrix.labels.map((lbl, idx) => (
                        <th key={idx} className="p-2.5 font-semibold">{lbl}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.evaluation_metrics.confusion_matrix.matrix.map((row, rIdx) => (
                      <tr key={rIdx} className="border-t border-[#E6E1D8] hover:bg-[#FBF9F5]">
                        <td className="p-2.5 text-left font-bold text-[#1A1E1C] bg-[#F4F1EA]">
                          {data.evaluation_metrics.confusion_matrix.labels[rIdx]}
                        </td>
                        {row.map((val, cIdx) => (
                          <td
                            key={cIdx}
                            className={`p-2.5 font-mono ${
                              rIdx === cIdx ? 'bg-[#DCFCE7] font-bold text-[#166534]' : 'text-[#737E79]'
                            }`}
                          >
                            {val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* Section 3: Model Cards */}
          <section className="editorial-card p-6 sm:p-8 space-y-6 bg-[#FFFFFF]">
            <div className="pb-4 border-b border-[#F4F1EA]">
              <h2 className="font-editorial text-xl font-bold text-[#1A1E1C] flex items-center gap-2">
                <Cpu className="w-5 h-5 text-[#1B3B2B]" />
                <span>System Model Cards & Component Architecture</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {data.model_cards.map((card, idx) => (
                <div key={idx} className="p-5 bg-[#FBF9F5] rounded-md border border-[#E6E1D8] space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <span className="font-mono text-[10px] uppercase font-bold text-[#1B3B2B] bg-[#EAF2ED] px-2 py-0.5 rounded border border-[#C5DDD0] inline-block">
                      {card.hardware} &bull; {card.latency_ms}
                    </span>
                    <h3 className="font-editorial text-base font-bold text-[#1A1E1C]">
                      {card.name}
                    </h3>
                    <p className="text-xs text-[#4A5450] leading-relaxed">
                      {card.purpose}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-[#E6E1D8] space-y-2 text-[11px]">
                    <div>
                      <span className="font-semibold text-[#1B7A43] block">Key Strength:</span>
                      <span className="text-[#5C6661]">{card.strengths}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-[#9B2C2C] block">Known Limitation:</span>
                      <span className="text-[#5C6661]">{card.limitations}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
};
