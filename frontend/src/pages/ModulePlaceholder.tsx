import React from 'react';
import { EmptyState } from '../components/EmptyState';
import { LucideIcon, Layers, Database, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ModulePlaceholderProps {
  title: string;
  subtitle: string;
  stageBadge?: string;
  icon?: LucideIcon;
  targetStage: string;
  plannedFeatures: string[];
  dbDependencies: string[];
}

export const ModulePlaceholder: React.FC<ModulePlaceholderProps> = ({
  title,
  subtitle,
  stageBadge = 'Slated for Stage 2 / 3',
  icon: Icon = Layers,
  targetStage,
  plannedFeatures,
  dbDependencies,
}) => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700 mb-2">
          {targetStage}
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">{title}</h2>
        <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
      </div>

      {/* Main Empty State */}
      <EmptyState
        title={`${title} Module Foundation Ready`}
        description={`This module relies on clean data from the Brazilian E-Commerce dataset. In adherence to production principles, no fake charts, fabricated predictions, or placeholder mock KPIs are generated until ETL ingestion and statistical modeling pipelines run in ${targetStage}.`}
        stageBadge={stageBadge}
        actionText="Inspect Data Ingestion Health"
        actionLink="/data-quality"
        icon={<Icon className="h-7 w-7 text-indigo-400" />}
      />

      {/* Specification Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Planned Analytical Capabilities */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">
            Planned Analytical Capabilities
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {plannedFeatures.map((feat, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0" />
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Database Prerequisites */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
            <Database className="h-3.5 w-3.5 text-indigo-400" />
            Relational Schema Prerequisites
          </h3>
          <p className="text-[11px] text-slate-400 mb-3">
            All necessary tables and foreign key constraints have been built in Stage 1 and are awaiting CSV ingestion:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {dbDependencies.map((table, idx) => (
              <span
                key={idx}
                className="px-2 py-1 rounded bg-slate-950 text-indigo-300 font-mono text-[11px] border border-slate-800"
              >
                {table}
              </span>
            ))}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80">
            <Link
              to="/data-quality"
              className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              Verify table schemas in Data Quality <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
