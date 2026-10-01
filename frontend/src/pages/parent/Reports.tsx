import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ReportSummary } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/States';
import { FileText, Printer, Shield, CheckCircle, AlertTriangle } from 'lucide-react';

export const Reports: React.FC = () => {
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const res = await api.get('/parent/reports');
        setReport(res.data);
      } catch (err) {
        console.error('Failed to load safety report', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, []);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Compiling formal safety audit report..." />;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto print:p-0 print:m-0">
      {/* Action Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10 print:hidden">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <span>Child Digital Safety Audit Report</span>
          </h1>
          <p className="text-xs text-slate-400">
            Formal telemetry summary suitable for parental review or counseling context.
          </p>
        </div>
        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs shadow-md transition-colors cursor-pointer"
        >
          <Printer className="w-4 h-4" />
          <span>Print / Export PDF</span>
        </button>
      </div>

      {/* Printable Report Document */}
      <div className="glass-card p-8 border-white/10 space-y-6 print:bg-white print:text-black print:border-none print:shadow-none">
        {/* Document Header */}
        <div className="flex items-start justify-between border-b border-white/10 pb-6 print:border-black">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Shield className="w-5 h-5 text-cyan-400 print:text-black" />
              <span className="font-bold font-mono text-sm tracking-widest text-white print:text-black">
                CHILD-SAFE DIGITAL PLATFORM
              </span>
            </div>
            <h2 className="text-lg font-bold text-slate-100 print:text-black">
              Comprehensive Safety Telemetry Assessment
            </h2>
            <p className="text-xs text-slate-400 print:text-gray-600 mt-1">
              Generated: {new Date(report?.generated_at || '').toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-white/5 border border-white/10 text-cyan-300 print:border-black print:text-black">
              OFFICIAL MAJOR PROJECT AUDIT
            </span>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="space-y-2">
          <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider print:text-black">
            Executive Safety Summary
          </h3>
          <p className="text-xs text-slate-300 print:text-black leading-relaxed">
            During the monitoring cycle, <strong>{report?.total_messages || 0} messages</strong> across{' '}
            <strong>{report?.conversations?.length || 0} separate peer channels</strong> were analyzed by the multi-layer
            risk detection pipeline. The system identified{' '}
            <strong className="text-orange-400 print:text-black">{report?.total_alerts || 0} safety alerts</strong>{' '}
            requiring review.
          </p>
        </div>

        {/* Channel Risk Breakdown */}
        <div className="space-y-3">
          <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider print:text-black">
            Channel Risk Matrix
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-white/10 print:border-gray-300 rounded-lg overflow-hidden">
              <thead className="bg-white/5 print:bg-gray-100 font-mono text-slate-400 print:text-black border-b border-white/10 print:border-gray-300">
                <tr>
                  <th className="p-2.5">Channel ID</th>
                  <th className="p-2.5">Participant</th>
                  <th className="p-2.5">Messages</th>
                  <th className="p-2.5">Risk Score</th>
                  <th className="p-2.5">Assessment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 print:divide-gray-200">
                {report?.conversations?.map((conv) => (
                  <tr key={conv.conversation_id} className="hover:bg-white/[0.02]">
                    <td className="p-2.5 font-mono text-slate-400 print:text-gray-700">
                      {conv.conversation_id}
                    </td>
                    <td className="p-2.5 font-semibold text-slate-200 print:text-black">
                      {conv.contact_name}
                    </td>
                    <td className="p-2.5 font-mono text-slate-300 print:text-black">
                      {conv.message_count}
                    </td>
                    <td className="p-2.5 font-mono font-bold text-white print:text-black">
                      {conv.risk_score}%
                    </td>
                    <td className="p-2.5">
                      <StatusBadge severity={conv.severity} size="sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category Distribution */}
        {report?.category_distribution && Object.keys(report.category_distribution).length > 0 && (
          <div className="space-y-2">
            <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider print:text-black">
              Flagged Risk Categories
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(report.category_distribution).map(([cat, count]) => (
                <div
                  key={cat}
                  className="p-2.5 rounded-lg bg-black/20 border border-white/5 print:border-gray-300 flex justify-between items-center text-xs"
                >
                  <span className="text-slate-300 print:text-black capitalize font-medium">
                    {cat.toLowerCase().replace('_', ' ')}
                  </span>
                  <span className="font-mono text-cyan-400 print:text-black font-bold">
                    {count} incident(s)
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Privacy & Methodology Statement (Requirement #37, #63) */}
        <div className="pt-4 border-t border-white/10 print:border-gray-300 text-[11px] text-slate-400 print:text-gray-600 space-y-1.5">
          <p className="font-semibold text-slate-300 print:text-black">Privacy Notice & Technical Disclaimer</p>
          <p className="leading-relaxed">
            In accordance with privacy-first standards, raw conversation contents are preserved privately and not
            automatically displayed in reports. Risk scoring represents probabilistic AI-assisted analysis using rules,
            TF-IDF ML classification, and behavioral telemetry to highlight potential conversational patterns.
          </p>
        </div>
      </div>
    </div>
  );
};
