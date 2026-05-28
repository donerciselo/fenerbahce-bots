import React, { useState } from 'react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

interface ViolationLog {
  id: string;
  timestamp: string;
  user: string;
  riskScore: number;
  content: string;
  category: 'Hate' | 'Spam' | 'Fraud' | 'Leaked Info';
}

const initialLogs: ViolationLog[] = [
  { id: '001', timestamp: '16:11:02', user: '@vortex_null', riskScore: 0.94, content: 'SQL injection payload detected in text input parameter: UNION SELECT username, password FROM users--', category: 'Fraud' },
  { id: '002', timestamp: '16:08:45', user: '@krypton99', riskScore: 0.72, content: 'Repeated promotional distribution across 14 channels within 3.2 seconds.', category: 'Spam' },
  { id: '003', timestamp: '15:59:12', user: '@0xAlpha', riskScore: 0.88, content: 'Unusual high-frequency PII sequence detected matching pattern format: [DELETED_SSN_PATTERN].', category: 'Leaked Info' }
];

export default function ModerationTerminal() {
  const [logs, setLogs] = useState<ViolationLog[]>(() => {
    const saved = localStorage.getItem('violationLogs');
    return saved ? JSON.parse(saved) : initialLogs;
  });

  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const resolveIncident = (id: string) => {
    const updated = logs.filter(log => log.id !== id);
    setLogs(updated);
    localStorage.setItem('violationLogs', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-[#fafafa] font-mono antialiased flex selection:bg-[#f4f4f5] selection:text-[#09090b]">

      <aside className="w-80 border-r border-[#27272a] p-8 flex flex-col justify-between tracking-tight">
        <div>
          <div className="flex items-center space-x-3 mb-16">
            <div className="h-3 w-3 rounded-full bg-[#ef4444] animate-pulse" />
            <h1 className="text-sm font-bold uppercase tracking-[0.2em] text-[#a1a1aa]">Aegis // Core</h1>
          </div>

          <nav className="space-y-6">
            <div>
              <p className="text-[10px] text-[#71717a] uppercase tracking-widest mb-3">Live Vectors</p>
              <ul className="space-y-2 text-xs">
                <li className="text-[#fafafa] cursor-pointer flex justify-between items-center py-1">
                  <span>All Incidents</span>
                  <span className="text-[10px] bg-[#27272a] px-1.5 py-0.5 rounded text-[#a1a1aa]">{logs.length}</span>
                </li>
                <li className="text-[#71717a] hover:text-[#fafafa] transition-colors cursor-pointer py-1">Neural Filter</li>
                <li className="text-[#71717a] hover:text-[#fafafa] transition-colors cursor-pointer py-1">Anomalous Nodes</li>
              </ul>
            </div>
          </nav>
        </div>

        <div className="text-[10px] text-[#27272a] font-sans">
          SYSTEM STATUS: OPTIMAL // 2026
        </div>
      </aside>

      <main className="flex-1 p-12 overflow-y-auto">
        <header className="mb-12 flex justify-between items-end border-b border-[#18181b] pb-6">
          <div>
            <span className="text-[10px] uppercase tracking-widest text-[#71717a]">Stream Overview</span>
            <h2 className="text-2xl font-light tracking-tighter mt-1 text-[#f4f4f5]">Real-time Violations</h2>
          </div>
          <div className="text-xs text-[#71717a]">
            Active Processing / <span className="text-[#fafafa]">98.4 eps</span>
          </div>
        </header>

        <section className="space-y-4">
          {logs.map((log) => (
            <div
              key={log.id}
              className="group relative border border-[#18181b] hover:border-[#27272a] bg-[#09090b] transition-all duration-300 p-6 flex items-start gap-8"
            >
              <div className="flex flex-col items-center justify-center min-w-[50px]">
                <span className="text-[10px] text-[#71717a] tracking-widest uppercase mb-1">Risk</span>
                <span className={`text-sm font-semibold ${log.riskScore > 0.85 ? 'text-[#ef4444]' : 'text-[#f59e0b]'}`}>
                  {(log.riskScore * 100).toFixed(0)}%
                </span>
              </div>

              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-[#a1a1aa] font-bold">{log.user}</span>
                  <span className="text-[#27272a]">•</span>
                  <span className="text-[#71717a] text-[10px]">{log.timestamp}</span>
                  <span className="ml-auto text-[10px] bg-[#18181b] text-[#a1a1aa] px-2 py-0.5 rounded uppercase tracking-wider border border-[#27272a]">
                    {log.category}
                  </span>
                </div>
                <p className="text-xs text-[#d4d4d8] leading-relaxed max-w-4xl break-all">
                  {log.content}
                </p>
              </div>

              <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 self-center">
                <DropdownMenu.Root>
                  <DropdownMenu.Trigger asChild>
                    <button className="bg-[#18181b] hover:bg-[#27272a] text-xs px-3 py-1.5 border border-[#27272a] text-[#fafafa] transition-colors">
                      Execute
                    </button>
                  </DropdownMenu.Trigger>

                  <DropdownMenu.Portal>
                    <DropdownMenu.Content
                      className="bg-[#09090b] border border-[#27272a] p-1 space-y-0.5 min-w-[120px] shadow-2xl z-50 font-mono"
                      sideOffset={5}
                      align="end"
                    >
                      <DropdownMenu.Item
                        onClick={() => resolveIncident(log.id)}
                        className="text-[11px] text-[#ef4444] hover:bg-[#18181b] p-2 outline-none cursor-pointer transition-colors"
                      >
                        [ BAN USER ]
                      </DropdownMenu.Item>
                      <DropdownMenu.Item
                        onClick={() => resolveIncident(log.id)}
                        className="text-[11px] text-[#a1a1aa] hover:bg-[#18181b] p-2 outline-none cursor-pointer transition-colors"
                      >
                        [ PURGE DATA ]
                      </DropdownMenu.Item>
                      <DropdownMenu.Separator className="h-[1px] bg-[#18181b] my-1" />
                      <DropdownMenu.Item
                        onClick={() => resolveIncident(log.id)}
                        className="text-[11px] text-[#71717a] hover:bg-[#18181b] p-2 outline-none cursor-pointer transition-colors"
                      >
                        Dismiss False Alert
                      </DropdownMenu.Item>
                    </DropdownMenu.Content>
                  </DropdownMenu.Portal>
                </DropdownMenu.Root>
              </div>

            </div>
          ))}

          {logs.length === 0 && (
            <div className="h-64 border border-dashed border-[#18181b] flex flex-col items-center justify-center text-xs text-[#71717a] tracking-wide">
              <span>QUEUE CLEAR // NO ACTIVE THREATS DETECTED</span>
            </div>
          )}
        </section>
      </main>

    </div>
  );
}