'use client';

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import {
  Play, Shield, FileSearch, Brain, TreePine, Zap, Trash2,
  FileText, FolderOpen, Save, Plus, Search, Replace,
  ChevronRight, ChevronDown, File, X, Check, AlertTriangle,
  Info, XCircle, CheckCircle, Loader2, Terminal, BookOpen,
  Copy, Download, RotateCcw, Maximize2, Minimize2, PanelLeftClose,
  PanelLeftOpen, PanelRightClose, PanelRightOpen,
  Layers, ShieldCheck, Bug, Lightbulb, GitBranch, Gauge,
  MessageSquare, Send, Bot, User
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from '@/hooks/use-toast';

// ============================================================
// Types
// ============================================================
interface FileTab {
  id: string;
  name: string;
  content: string;
  modified: boolean;
}

interface OutputEntry {
  type: 'info' | 'success' | 'warning' | 'error' | 'system';
  message: string;
  timestamp: number;
}

interface VerifyCheck {
  name: string;
  status: 'PASS' | 'FAIL' | 'WARN';
  message: string;
  details?: string[];
}

interface Exercise {
  id: number;
  title: string;
  description: string;
  template: string;
}

// ============================================================
// AICL Syntax Highlighter
// ============================================================
const AICL_KEYWORDS = [
  'Goal', 'Layer', 'Sublayer', 'Validation', 'Risk', 'Recovery',
  'Constraint', 'Entity', 'Behavior', 'Input', 'Output', 'Action',
  'Condition', 'When', 'Then', 'Event', 'On', 'Parallel', 'Optimize',
  'Priority', 'Learn', 'Adapt', 'Based', 'Security', 'Encrypt',
  'Protect', 'Native', 'Import'
];

const AICL_TYPES = [
  'string', 'integer', 'float', 'boolean', 'datetime',
  'list', 'dict', 'set', 'any', 'void', 'bytes'
];

function highlightAICL(code: string): string {
  const lines = code.split('\n');
  return lines.map(line => {
    // Comment
    const commentIdx = line.indexOf('#');
    if (commentIdx !== -1) {
      const before = line.substring(0, commentIdx);
      const comment = line.substring(commentIdx);
      return highlightLine(before) + `<span class="aicl-comment">${escapeHtml(comment)}</span>`;
    }
    return highlightLine(line);
  }).join('\n');
}

function highlightLine(line: string): string {
  let result = escapeHtml(line);

  // Keywords at start of line or after whitespace (word boundary)
  for (const kw of AICL_KEYWORDS) {
    const regex = new RegExp(`(^|\\s)(${kw})(?=[:\\s]|$)`, 'g');
    result = result.replace(regex, `$1<span class="aicl-keyword">${kw}</span>`);
  }

  // Types
  for (const t of AICL_TYPES) {
    const regex = new RegExp(`(\\s|^)(${t})(?=\\s|:|$)`, 'g');
    result = result.replace(regex, `$1<span class="aicl-type">${t}</span>`);
  }

  return result;
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ============================================================
// Default file content
// ============================================================
const DEFAULT_FILE = `# AICL - Architecture Compilation Language
# Start writing your AICL specification here

Goal:
Build an amazing application

Layer:
Main Application

Validation:
Application works correctly
`;

// ============================================================
// Main Page Component
// ============================================================
export default function AICLEditor() {
  // --- State ---
  const [files, setFiles] = useState<FileTab[]>([
    { id: 'untitled-1', name: 'untitled-1.aicl', content: DEFAULT_FILE, modified: false }
  ]);
  const [activeFileId, setActiveFileId] = useState('untitled-1');
  const [output, setOutput] = useState<OutputEntry[]>([]);
  const [replHistory, setReplHistory] = useState<OutputEntry[]>([]);
  const [replInput, setReplInput] = useState('');
  const [cursorPos, setCursorPos] = useState({ line: 1, col: 1 });
  const [isRunning, setIsRunning] = useState(false);
  const [targetLang, setTargetLang] = useState('python');
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(true);
  const [leftPanelTab, setLeftPanelTab] = useState<'files' | 'exercises'>('files');
  const [bottomPanelTab, setBottomPanelTab] = useState<'output' | 'repl' | 'exercises'>('output');
  const [examples, setExamples] = useState<{ id: string; name: string; title: string; description: string; source: string }[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [activeExercise, setActiveExercise] = useState<number | null>(null);
  const [findOpen, setFindOpen] = useState(false);
  const [findText, setFindText] = useState('');
  const [replaceText, setReplaceText] = useState('');
  const [fileCounter, setFileCounter] = useState(2);
  const [rightPanelContent, setRightPanelContent] = useState<'output' | 'tree' | 'code' | 'tests' | 'chat'>('output');
  const [treeData, setTreeData] = useState('');
  const [compiledCode, setCompiledCode] = useState('');
  const [testCode, setTestCode] = useState('');

  // --- AI Chat state ---
  interface AICLFileBlock {
    filename: string;
    code: string;
  }
  interface ChatMsg {
    role: 'user' | 'assistant';
    content: string;
    aiclFiles?: AICLFileBlock[]; // parsed :::AICL_FILE blocks
  }
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([
    { role: 'assistant', content: 'Hello! I\'m the AICL AI Assistant. I can help you write AICL specifications, understand concepts like the No-Orphan Property and Proof of Origin, and guide you through the editor.\n\nTry asking me: "Describe a todo app in AICL" or "Write a chat server specification"' },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const replInputRef = useRef<HTMLInputElement>(null);
  const findInputRef = useRef<HTMLInputElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  const activeFile = files.find(f => f.id === activeFileId) || files[0];

  // --- Initialize client-only state (avoids hydration mismatch) ---
  useEffect(() => {
    const now = Date.now();
    setOutput([{ type: 'system', message: 'AICL Web Editor v1.0.0 — Ready', timestamp: now }]);
    setReplHistory([{ type: 'system', message: 'AICL Interactive Shell — Type AICL statements or commands', timestamp: now }]);
  }, []);

  // --- Load examples and exercises on mount ---
  useEffect(() => {
    fetch('/api/examples').then(r => r.json()).then(data => {
      if (data.examples) setExamples(data.examples);
    }).catch(() => {});

    fetch('/api/exercises').then(r => r.json()).then(data => {
      if (data.exercises) setExercises(data.exercises);
    }).catch(() => {});
  }, []);

  // --- File operations ---
  const updateFileContent = useCallback((fileId: string, content: string) => {
    setFiles(prev => prev.map(f => f.id === fileId ? { ...f, content, modified: true } : f));
  }, []);

  const newFile = useCallback(() => {
    const id = `untitled-${fileCounter}`;
    const newTab: FileTab = {
      id,
      name: `${id}.aicl`,
      content: `# New AICL File\n\nGoal:\nDescribe your goal\n\nLayer:\nMain\n\nValidation:\nCheck correctness\n`,
      modified: false,
    };
    setFiles(prev => [...prev, newTab]);
    setActiveFileId(id);
    setFileCounter(prev => prev + 1);
  }, [fileCounter]);

  const closeFile = useCallback((fileId: string) => {
    setFiles(prev => {
      const newFiles = prev.filter(f => f.id !== fileId);
      if (newFiles.length === 0) {
        const id = `untitled-${fileCounter}`;
        newFiles.push({ id, name: `${id}.aicl`, content: DEFAULT_FILE, modified: false });
        setFileCounter(c => c + 1);
        setActiveFileId(id);
      } else if (fileId === activeFileId) {
        setActiveFileId(newFiles[0].id);
      }
      return newFiles;
    });
  }, [activeFileId, fileCounter]);

  const openExample = useCallback((example: typeof examples[0]) => {
    const id = `example-${example.id}`;
    const existing = files.find(f => f.id === id);
    if (existing) {
      setActiveFileId(id);
      return;
    }
    setFiles(prev => [...prev, {
      id,
      name: example.name,
      content: example.source,
      modified: false,
    }]);
    setActiveFileId(id);
  }, [files]);

  // --- Output helpers (declared first since used by other callbacks) ---
  const addOutput = useCallback((type: OutputEntry['type'], message: string) => {
    setOutput(prev => [...prev, { type, message, timestamp: Date.now() }]);
  }, []);

  const addReplLine = useCallback((type: OutputEntry['type'], message: string) => {
    setReplHistory(prev => [...prev, { type, message, timestamp: Date.now() }]);
  }, []);

  const clearOutput = useCallback(() => {
    setOutput([]);
    addOutput('system', 'Output cleared');
  }, [addOutput]);

  const openExercise = useCallback((exercise: Exercise) => {
    const id = `exercise-${exercise.id}`;
    const existing = files.find(f => f.id === id);
    if (existing) {
      setActiveFileId(id);
      return;
    }
    setFiles(prev => [...prev, {
      id,
      name: `exercise_${exercise.id}_${exercise.title.toLowerCase().replace(/\s+/g, '_')}.aicl`,
      content: exercise.template,
      modified: false,
    }]);
    setActiveFileId(id);
    setActiveExercise(exercise.id);
    setBottomPanelTab('exercises');
  }, [files]);

  const saveFile = useCallback(() => {
    const blob = new Blob([activeFile.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeFile.name;
    a.click();
    URL.revokeObjectURL(url);
    setFiles(prev => prev.map(f => f.id === activeFileId ? { ...f, modified: false } : f));
    addOutput('info', `File saved: ${activeFile.name}`);
  }, [activeFile, activeFileId, addOutput]);

  const loadFile = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.aicl,.txt';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (ev) => {
          const content = ev.target?.result as string;
          const id = `file-${Date.now()}`;
          setFiles(prev => [...prev, {
            id,
            name: file.name,
            content,
            modified: false,
          }]);
          setActiveFileId(id);
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }, []);

  // --- Toolbar actions ---
  const runCompile = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Compiling ${activeFile.name} → ${targetLang}...`);
    try {
      const res = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content, target: targetLang }),
      });
      const data = await res.json();

      if (data.success) {
        addOutput('success', `Compilation successful! (${data.stages_completed?.length || 0} stages)`);
        addOutput('info', `TODOs remaining: ${data.todos_remaining}`);
        addOutput('info', `Audit coverage: ${((data.audit_coverage || 0) * 100).toFixed(0)}%`);
        if (data.proof_valid) {
          addOutput('success', 'Proof of Origin: Valid ✓');
        }
        if (data.warnings?.length) {
          data.warnings.forEach((w: string) => addOutput('warning', `Warning: ${w}`));
        }
        addOutput('info', `Generated ${(data.main_code || '').split('\n').length} lines of ${targetLang} code`);
        // Store compiled code for Code tab
        setCompiledCode(data.main_code || '');
        setTestCode(data.test_code || '');
        if (data.tree) setTreeData(data.tree);
        setRightPanelContent('code');
      } else {
        addOutput('error', 'Compilation failed!');
        data.errors?.forEach((e: string) => addOutput('error', e));
      }
    } catch (err) {
      addOutput('error', `Compile error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, targetLang, addOutput]);

  const runVerify = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Verifying ${activeFile.name}...`);
    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();
      addOutput(data.overall === 'PASS' ? 'success' : data.overall === 'ERROR' ? 'error' : 'warning',
        `Verification: ${data.overall} (${data.passed || 0} passed, ${data.warnings || 0} warnings, ${data.failed || 0} failed)`);
      data.checks?.forEach((c: VerifyCheck) => {
        const icon = c.status === 'PASS' ? '✓' : c.status === 'FAIL' ? '✗' : '⚠';
        addOutput(
          c.status === 'PASS' ? 'success' : c.status === 'FAIL' ? 'error' : 'warning',
          `${icon} ${c.name}: ${c.message}`
        );
      });
      setRightPanelContent('output');
    } catch (err) {
      addOutput('error', `Verify error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, addOutput]);

  const runAudit = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Auditing ${activeFile.name}...`);
    try {
      const res = await fetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();
      if (data.error) {
        addOutput('error', `Audit error: ${data.error}`);
      } else {
        const coveragePercent = ((data.coverage || 0) * 100).toFixed(1);
        addOutput('success', `Audit Coverage: ${coveragePercent}%`);
        addOutput('info', `Total artifacts: ${data.total_artifacts || 0}`);
        addOutput('info', `With provenance: ${data.artifacts_with_provenance || 0}`);
        addOutput(data.orphan_count > 0 ? 'warning' : 'success',
          `Orphan artifacts: ${data.orphan_count || 0}`);
        if (data.orphan_names?.length) {
          data.orphan_names.forEach((n: string) => addOutput('warning', `  Orphan: ${n}`));
        }
      }
      setRightPanelContent('output');
    } catch (err) {
      addOutput('error', `Audit error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, addOutput]);

  const runExplain = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Explaining ${activeFile.name}...`);
    try {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();
      if (data.error) {
        addOutput('error', `Explain error: ${data.error}`);
      } else {
        addOutput('success', `Provenance: ${data.total_records || 0} decision records`);
        data.decisions?.forEach((d: { type: string; source: string; confidence: number; pattern?: string }) => {
          addOutput('info', `  [${d.type}] ${d.source} (confidence: ${(d.confidence * 100).toFixed(0)}%)${d.pattern ? ` via ${d.pattern}` : ''}`);
        });
      }
      setRightPanelContent('output');
    } catch (err) {
      addOutput('error', `Explain error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, addOutput]);

  const runTree = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Generating architecture tree for ${activeFile.name}...`);
    try {
      const res = await fetch('/api/tree', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();
      if (data.error) {
        addOutput('error', `Tree error: ${data.error}`);
      } else {
        addOutput('success', 'Architecture tree generated');
        setRightPanelContent('tree');
      }
    } catch (err) {
      addOutput('error', `Tree error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, addOutput]);

  const runOptimize = useCallback(async () => {
    setIsRunning(true);
    addOutput('info', `Optimizing ${activeFile.name}...`);
    try {
      const res = await fetch('/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();
      if (data.error) {
        addOutput('error', `Optimize error: ${data.error}`);
      } else {
        addOutput('success', `Optimization complete (score: ${((data.improvement_score || 0) * 100).toFixed(0)}%)`);
        data.actions?.forEach((a: { type: string; description: string; risk: string; affected_elements?: string[] }) => {
          addOutput('info', `  [${a.type}] ${a.description} (risk: ${a.risk})`);
        });
      }
      setRightPanelContent('output');
    } catch (err) {
      addOutput('error', `Optimize error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setIsRunning(false);
  }, [activeFile, addOutput]);

  // --- REPL ---
  const handleReplSubmit = useCallback(async () => {
    const cmd = replInput.trim();
    if (!cmd) return;

    addReplLine('info', `>>> ${cmd}`);
    setReplInput('');

    if (cmd.startsWith(':')) {
      const parts = cmd.slice(1).split(/\s+/);
      const command = parts[0];
      const args = parts.slice(1);

      switch (command) {
        case 'help':
          addReplLine('system', 'AICL Shell Commands:');
          addReplLine('system', '  :help           - Show this help');
          addReplLine('system', '  :compile [lang] - Compile current file (python/rust/javascript/go)');
          addReplLine('system', '  :verify         - Verify current file');
          addReplLine('system', '  :audit          - Audit current file');
          addReplLine('system', '  :explain        - Explain provenance');
          addReplLine('system', '  :tree           - Show architecture tree');
          addReplLine('system', '  :optimize       - Optimize architecture');
          addReplLine('system', '  :clear          - Clear shell');
          addReplLine('system', '  :load <name>    - Load example file');
          addReplLine('system', '  :exercises      - List exercises');
          break;
        case 'compile':
          setTargetLang(args[0] || 'python');
          // Trigger compile
          addReplLine('info', `Compiling to ${args[0] || 'python'}...`);
          try {
            const res = await fetch('/api/compile', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content, target: args[0] || 'python' }),
            });
            const data = await res.json();
            if (data.success) {
              addReplLine('success', 'Compilation successful!');
              addReplLine('info', data.main_code?.split('\n').slice(0, 5).join('\n') + '\n...');
            } else {
              addReplLine('error', 'Compilation failed');
              data.errors?.forEach((e: string) => addReplLine('error', e));
            }
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        case 'verify': {
          try {
            const res = await fetch('/api/verify', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content }),
            });
            const data = await res.json();
            addReplLine(data.overall === 'PASS' ? 'success' : 'warning', `Verification: ${data.overall}`);
            data.checks?.forEach((c: VerifyCheck) => {
              addReplLine(c.status === 'PASS' ? 'success' : c.status === 'FAIL' ? 'error' : 'warning',
                `  ${c.status} ${c.name}: ${c.message}`);
            });
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'audit': {
          try {
            const res = await fetch('/api/audit', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content }),
            });
            const data = await res.json();
            addReplLine('success', `Audit coverage: ${((data.coverage || 0) * 100).toFixed(1)}%`);
            addReplLine('info', `Artifacts: ${data.total_artifacts}, Orphans: ${data.orphan_count}`);
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'tree': {
          try {
            const res = await fetch('/api/tree', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content }),
            });
            const data = await res.json();
            if (data.tree) {
              data.tree.split('\n').forEach((line: string) => addReplLine('info', line));
            }
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'optimize': {
          try {
            const res = await fetch('/api/optimize', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content }),
            });
            const data = await res.json();
            addReplLine('success', `Optimization score: ${((data.improvement_score || 0) * 100).toFixed(0)}%`);
            data.actions?.forEach((a: { type: string; description: string; risk: string }) => {
              addReplLine('info', `  [${a.type}] ${a.description}`);
            });
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'explain': {
          try {
            const res = await fetch('/api/explain', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content }),
            });
            const data = await res.json();
            addReplLine('success', `${data.total_records} provenance records`);
            data.decisions?.slice(0, 10).forEach((d: { type: string; source: string; confidence: number }) => {
              addReplLine('info', `  [${d.type}] ${d.source} (${(d.confidence * 100).toFixed(0)}%)`);
            });
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'clear':
          setReplHistory([]);
          break;
        case 'load': {
          const exName = args[0];
          const ex = examples.find(e => e.id === exName || e.name.includes(exName));
          if (ex) {
            openExample(ex);
            addReplLine('success', `Loaded: ${ex.name}`);
          } else {
            addReplLine('error', `Example not found: ${exName}`);
            addReplLine('info', `Available: ${examples.map(e => e.id).join(', ')}`);
          }
          break;
        }
        case 'exercises':
          exercises.forEach(ex => {
            addReplLine('info', `  ${ex.id}. ${ex.title}`);
          });
          break;
        default:
          addReplLine('error', `Unknown command: :${command}. Type :help for available commands.`);
      }
    } else {
      // Try to parse as AICL
      try {
        const res = await fetch('/api/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: cmd }),
        });
        const data = await res.json();
        if (data.overall === 'PASS' || data.overall === 'FAIL') {
          addReplLine(data.overall === 'PASS' ? 'success' : 'warning', `Parsed: ${data.overall}`);
          data.checks?.forEach((c: VerifyCheck) => {
            addReplLine(c.status === 'PASS' ? 'success' : 'warning', `  ${c.status} ${c.name}`);
          });
        }
      } catch {
        addReplLine('error', 'Parse error');
      }
    }
  }, [replInput, activeFile, examples, exercises, openExample, addReplLine]);

  // --- Editor key handling ---
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const ta = e.currentTarget;

    // Tab → insert 4 spaces
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const content = activeFile.content;
      if (e.shiftKey) {
        // Shift+Tab: remove 4 spaces
        const lineStart = content.lastIndexOf('\n', start - 1) + 1;
        const line = content.substring(lineStart, start);
        if (line.startsWith('    ')) {
          const newContent = content.substring(0, lineStart) + content.substring(lineStart + 4);
          updateFileContent(activeFileId, newContent);
          setTimeout(() => {
            ta.selectionStart = ta.selectionEnd = start - 4;
          }, 0);
        }
      } else {
        const newContent = content.substring(0, start) + '    ' + content.substring(end);
        updateFileContent(activeFileId, newContent);
        setTimeout(() => {
          ta.selectionStart = ta.selectionEnd = start + 4;
        }, 0);
      }
      return;
    }

    // Enter → auto-indent
    if (e.key === 'Enter') {
      e.preventDefault();
      const start = ta.selectionStart;
      const content = activeFile.content;
      const lineStart = content.lastIndexOf('\n', start - 1) + 1;
      const currentLine = content.substring(lineStart, start);
      const indent = currentLine.match(/^\s*/)?.[0] || '';

      // If the line ends with a colon, add extra indent
      const trimmedLine = currentLine.trimEnd();
      const needsIndent = trimmedLine.endsWith(':');

      const newIndent = needsIndent ? indent + '    ' : indent;
      const newContent = content.substring(0, start) + '\n' + newIndent + content.substring(ta.selectionEnd);
      updateFileContent(activeFileId, newContent);
      setTimeout(() => {
        ta.selectionStart = ta.selectionEnd = start + 1 + newIndent.length;
      }, 0);
      return;
    }

    // Ctrl+S → Save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      saveFile();
      return;
    }

    // Ctrl+F → Find
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
      e.preventDefault();
      setFindOpen(true);
      setTimeout(() => findInputRef.current?.focus(), 50);
      return;
    }

    // Ctrl+H → Replace
    if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
      e.preventDefault();
      setFindOpen(true);
      return;
    }

    // Escape → Close find
    if (e.key === 'Escape') {
      setFindOpen(false);
    }
  }, [activeFile, activeFileId, updateFileContent, saveFile]);

  // --- Cursor position tracking ---
  const handleCursorChange = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    const pos = ta.selectionStart;
    const content = ta.value;
    const lines = content.substring(0, pos).split('\n');
    setCursorPos({ line: lines.length, col: lines[lines.length - 1].length + 1 });
  }, []);

  // --- Auto-complete ---
  const handleAutoComplete = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    const pos = ta.selectionStart;
    const content = activeFile.content;
    const lineStart = content.lastIndexOf('\n', pos - 1) + 1;
    const textBefore = content.substring(lineStart, pos);
    const wordMatch = textBefore.match(/(\w+)$/);
    if (!wordMatch) return;

    const word = wordMatch[1];
    if (word.length < 2) return;

    const match = AICL_KEYWORDS.find(k => k.toLowerCase().startsWith(word.toLowerCase()) && k !== word);
    if (match) {
      const completion = match.substring(word.length);
      const newContent = content.substring(0, pos) + completion + content.substring(pos);
      updateFileContent(activeFileId, newContent);
      setTimeout(() => {
        ta.selectionStart = ta.selectionEnd = pos + completion.length;
      }, 0);
    }
  }, [activeFile, activeFileId, updateFileContent]);

  // --- Find/Replace ---
  const handleFindNext = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta || !findText) return;
    const content = activeFile.content;
    const startFrom = ta.selectionEnd;
    const idx = content.indexOf(findText, startFrom);
    if (idx >= 0) {
      ta.focus();
      ta.setSelectionRange(idx, idx + findText.length);
    } else {
      // Wrap around
      const idx2 = content.indexOf(findText);
      if (idx2 >= 0) {
        ta.focus();
        ta.setSelectionRange(idx2, idx2 + findText.length);
      } else {
        toast({ title: 'Not found', description: `"${findText}" not found` });
      }
    }
  }, [activeFile, findText]);

  const handleReplaceAll = useCallback(() => {
    if (!findText) return;
    const newContent = activeFile.content.replaceAll(findText, replaceText);
    updateFileContent(activeFileId, newContent);
    addOutput('info', `Replaced all occurrences of "${findText}" with "${replaceText}"`);
  }, [activeFile, activeFileId, findText, replaceText, updateFileContent, addOutput]);

  // --- Highlighted code for overlay ---
  const highlightedCode = useMemo(() => highlightAICL(activeFile.content), [activeFile.content]);

  // --- Line numbers ---
  const lineNumbers = useMemo(() => {
    const count = activeFile.content.split('\n').length;
    return Array.from({ length: count }, (_, i) => i + 1);
  }, [activeFile.content]);

  // --- Check exercise ---
  const checkExercise = useCallback(async () => {
    if (!activeExercise) return;
    setIsRunning(true);
    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      });
      const data = await res.json();

      // Check if TODOs are still present
      const hasTodos = activeFile.content.includes('TODO');

      if (hasTodos) {
        toast({
          title: 'Exercise Incomplete',
          description: 'Some TODO items remain. Complete them before checking.',
          variant: 'destructive',
        });
      } else if (data.overall === 'PASS') {
        toast({
          title: 'Exercise Complete! 🎉',
          description: 'Your AICL specification passes all verification checks.',
        });
      } else {
        toast({
          title: 'Verification Issues',
          description: `Your spec has ${data.failed || 0} failing checks. Review and fix them.`,
          variant: 'destructive',
        });
      }
    } catch {
      toast({ title: 'Error', description: 'Could not check exercise', variant: 'destructive' });
    }
    setIsRunning(false);
  }, [activeExercise, activeFile]);

  // --- AI Chat ---
  // Parse :::AICL_FILE blocks from AI response
  const parseAICLFiles = (text: string): { cleanText: string; files: { filename: string; code: string }[] } => {
    const files: { filename: string; code: string }[] = [];
    const regex = /:::AICL_FILE\s+(\S+)\n([\s\S]*?):::END_FILE/g;
    let match;
    while ((match = regex.exec(text)) !== null) {
      files.push({ filename: match[1], code: match[2].trim() });
    }
    const cleanText = text.replace(regex, '').trim();
    return { cleanText, files };
  };

  const sendChatMessage = useCallback(async () => {
    const msg = chatInput.trim();
    if (!msg || chatLoading) return;

    const userMessage: ChatMsg = { role: 'user', content: msg };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...chatMessages, userMessage].map(m => ({ role: m.role, content: m.content })),
          context: activeFile.content,
        }),
      });
      const data = await res.json();
      const rawMessage = data.message || 'Sorry, I could not generate a response.';
      const { cleanText, files } = parseAICLFiles(rawMessage);

      const assistantMessage: ChatMsg = {
        role: 'assistant',
        content: files.length > 0 ? cleanText : rawMessage,
        aiclFiles: files.length > 0 ? files : undefined,
      };
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }]);
    }
    setChatLoading(false);
  }, [chatInput, chatLoading, chatMessages, activeFile.content]);

  // Chat action: create file from AICL block
  const chatCreateFile = useCallback((filename: string, code: string) => {
    const id = `chat-${Date.now()}`;
    setFiles(prev => [...prev, { id, name: filename, content: code, modified: false }]);
    setActiveFileId(id);
    setFileCounter(prev => prev + 1);
    addOutput('info', `Created file from AI: ${filename}`);
    toast({ title: 'File Created', description: `${filename} has been created from the AI response.` });
  }, [addOutput]);

  // Chat action: create file AND compile
  const chatCreateAndCompile = useCallback(async (filename: string, code: string) => {
    chatCreateFile(filename, code);
    // Small delay to ensure state is updated, then compile
    setTimeout(async () => {
      setIsRunning(true);
      addOutput('info', `Compiling ${filename} → ${targetLang}...`);
      try {
        const res = await fetch('/api/compile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: code, target: targetLang }),
        });
        const data = await res.json();
        if (data.success) {
          addOutput('success', `Compilation successful! (${data.stages_completed?.length || 0} stages)`);
          addOutput('info', `Audit coverage: ${((data.audit_coverage || 0) * 100).toFixed(0)}%`);
          if (data.proof_valid) addOutput('success', 'Proof of Origin: Valid ✓');
          setCompiledCode(data.main_code || '');
          setTestCode(data.test_code || '');
          if (data.tree) setTreeData(data.tree);
          setRightPanelContent('code');
        } else {
          addOutput('error', 'Compilation failed!');
          data.errors?.forEach((e: string) => addOutput('error', e));
        }
      } catch (err) {
        addOutput('error', `Compile error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
      setIsRunning(false);
    }, 200);
  }, [chatCreateFile, targetLang, addOutput]);

  // Chat action: create file AND verify
  const chatCreateAndVerify = useCallback(async (filename: string, code: string) => {
    chatCreateFile(filename, code);
    setTimeout(async () => {
      setIsRunning(true);
      addOutput('info', `Verifying ${filename}...`);
      try {
        const res = await fetch('/api/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: code }),
        });
        const data = await res.json();
        addOutput(data.overall === 'PASS' ? 'success' : data.overall === 'ERROR' ? 'error' : 'warning',
          `Verification: ${data.overall} (${data.passed || 0} passed, ${data.warnings || 0} warnings, ${data.failed || 0} failed)`);
        data.checks?.forEach((c: VerifyCheck) => {
          const icon = c.status === 'PASS' ? '✓' : c.status === 'FAIL' ? '✗' : '⚠';
          addOutput(c.status === 'PASS' ? 'success' : c.status === 'FAIL' ? 'error' : 'warning',
            `${icon} ${c.name}: ${c.message}`);
        });
        setRightPanelContent('output');
      } catch (err) {
        addOutput('error', `Verify error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
      setIsRunning(false);
    }, 200);
  }, [chatCreateFile, addOutput]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Load tree when panel opens
  useEffect(() => {
    if (rightPanelContent === 'tree' && !treeData) {
      fetch('/api/tree', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content }),
      }).then(r => r.json()).then(data => {
        setTreeData(data.tree || data.error || 'No tree data');
      }).catch(() => setTreeData('Error loading tree'));
    }
  }, [rightPanelContent, activeFile.content, treeData]);

  // ============================================================
  // RENDER
  // ============================================================
  return (
    <TooltipProvider delayDuration={300}>
      <div className="h-screen flex flex-col bg-[#1e1e1e] text-[#d4d4d4] overflow-hidden">
        {/* ======== TOOLBAR ======== */}
        <div className="flex items-center gap-1 px-2 py-1 bg-[#252526] border-b border-[#3c3c3c] flex-shrink-0">
          {/* Left: Logo + File ops */}
          <div className="flex items-center gap-1 mr-2">
            <div className="flex items-center gap-1.5 px-2">
              <div className="w-4 h-4 rounded bg-[#cd2d48] flex items-center justify-center">
                <span className="text-white text-[8px] font-bold">A</span>
              </div>
              <span className="text-xs font-semibold text-[#cd2d48]">AICL</span>
            </div>
            <div className="w-px h-4 bg-[#3c3c3c]" />
          </div>

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30]" onClick={newFile}><Plus className="h-3.5 w-3.5 mr-1" />New</Button></TooltipTrigger><TooltipContent>New File</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30]" onClick={loadFile}><FolderOpen className="h-3.5 w-3.5 mr-1" />Open</Button></TooltipTrigger><TooltipContent>Open File</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30]" onClick={saveFile}><Save className="h-3.5 w-3.5 mr-1" />Save</Button></TooltipTrigger><TooltipContent>Save (Ctrl+S)</TooltipContent></Tooltip>

          <div className="w-px h-4 bg-[#3c3c3c] mx-1" />

          {/* Target language selector */}
          <Select value={targetLang} onValueChange={setTargetLang}>
            <SelectTrigger className="h-7 w-[110px] text-xs bg-[#2d2d30] border-[#3c3c3c]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#252526] border-[#3c3c3c]">
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="rust">Rust</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
              <SelectItem value="go">Go</SelectItem>
            </SelectContent>
          </Select>

          <div className="w-px h-4 bg-[#3c3c3c] mx-1" />

          {/* AICL Actions */}
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#4ec9b0]" onClick={runCompile} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <Play className="h-3.5 w-3.5 mr-1" />}Compile</Button></TooltipTrigger><TooltipContent>Compile AICL source code</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#569cd6]" onClick={runVerify} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <ShieldCheck className="h-3.5 w-3.5 mr-1" />}Verify</Button></TooltipTrigger><TooltipContent>Verify specification quality</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#dcdcaa]" onClick={runAudit} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <FileSearch className="h-3.5 w-3.5 mr-1" />}Audit</Button></TooltipTrigger><TooltipContent>Audit compilation provenance</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#c586c0]" onClick={runExplain} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <Brain className="h-3.5 w-3.5 mr-1" />}Explain</Button></TooltipTrigger><TooltipContent>Explain compilation provenance</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#6a9955]" onClick={runTree} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <TreePine className="h-3.5 w-3.5 mr-1" />}Tree</Button></TooltipTrigger><TooltipContent>Architecture tree</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#ce9178]" onClick={runOptimize} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> : <Zap className="h-3.5 w-3.5 mr-1" />}Optimize</Button></TooltipTrigger><TooltipContent>Optimize architecture</TooltipContent></Tooltip>

          <div className="w-px h-4 bg-[#3c3c3c] mx-1" />

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30] text-[#c586c0]" onClick={() => { setRightPanelOpen(true); setRightPanelContent('chat'); setTimeout(() => chatInputRef.current?.focus(), 100); }}><MessageSquare className="h-3.5 w-3.5 mr-1" />AI Chat</Button></TooltipTrigger><TooltipContent>Open AI Assistant chat</TooltipContent></Tooltip>

          <div className="w-px h-4 bg-[#3c3c3c] mx-1" />

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30]" onClick={clearOutput}><Trash2 className="h-3.5 w-3.5 mr-1" />Clear</Button></TooltipTrigger><TooltipContent>Clear output</TooltipContent></Tooltip>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Right: Search */}
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2 text-xs hover:bg-[#2d2d30]" onClick={() => { setFindOpen(!findOpen); setTimeout(() => findInputRef.current?.focus(), 50); }}><Search className="h-3.5 w-3.5 mr-1" />Find</Button></TooltipTrigger><TooltipContent>Find & Replace (Ctrl+F)</TooltipContent></Tooltip>
        </div>

        {/* ======== FILE TABS ======== */}
        <div className="flex items-center bg-[#252526] border-b border-[#3c3c3c] flex-shrink-0 overflow-x-auto">
          {files.map(file => (
            <div
              key={file.id}
              className={`flex items-center gap-1 px-3 py-1.5 text-xs cursor-pointer border-r border-[#3c3c3c] group min-w-0 ${
                file.id === activeFileId ? 'bg-[#1e1e1e] text-white border-t-2 border-t-[#cd2d48]' : 'bg-[#2d2d30] text-[#808080] hover:bg-[#2d2d30]'
              }`}
              onClick={() => setActiveFileId(file.id)}
            >
              <File className="h-3 w-3 text-[#4ec9b0] flex-shrink-0" />
              <span className="truncate max-w-[120px]">{file.name}</span>
              {file.modified && <span className="w-2 h-2 rounded-full bg-[#cd2d48] flex-shrink-0" />}
              <button
                className="ml-1 opacity-0 group-hover:opacity-100 hover:text-white flex-shrink-0"
                onClick={(e) => { e.stopPropagation(); closeFile(file.id); }}
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
          <button
            className="px-2 py-1.5 text-[#808080] hover:text-white hover:bg-[#2d2d30] text-xs"
            onClick={newFile}
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* ======== FIND/REPLACE BAR ======== */}
        {findOpen && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#252526] border-b border-[#3c3c3c] flex-shrink-0">
            <div className="flex items-center gap-1 flex-1">
              <Search className="h-3.5 w-3.5 text-[#808080]" />
              <input
                ref={findInputRef}
                className="bg-[#3c3c3c] border border-[#4f4f4f] rounded px-2 py-1 text-xs text-[#d4d4d4] w-48 focus:outline-none focus:border-[#cd2d48]"
                placeholder="Find..."
                value={findText}
                onChange={(e) => setFindText(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleFindNext(); if (e.key === 'Escape') setFindOpen(false); }}
              />
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={handleFindNext}>Next</Button>
            </div>
            <div className="flex items-center gap-1 flex-1">
              <Replace className="h-3.5 w-3.5 text-[#808080]" />
              <input
                className="bg-[#3c3c3c] border border-[#4f4f4f] rounded px-2 py-1 text-xs text-[#d4d4d4] w-48 focus:outline-none focus:border-[#cd2d48]"
                placeholder="Replace..."
                value={replaceText}
                onChange={(e) => setReplaceText(e.target.value)}
              />
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={handleReplaceAll}>Replace All</Button>
            </div>
            <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => setFindOpen(false)}>
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        )}

        {/* ======== MAIN CONTENT ======== */}
        <div className="flex-1 flex overflow-hidden">
          {/* --- Left Panel --- */}
          {leftPanelOpen && (
            <>
              <div className="w-60 bg-[#252526] border-r border-[#3c3c3c] flex flex-col flex-shrink-0 overflow-hidden">
                {/* Panel Tabs */}
                <div className="flex border-b border-[#3c3c3c]">
                  <button
                    className={`flex-1 px-3 py-2 text-xs font-medium ${leftPanelTab === 'files' ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808080] hover:text-[#d4d4d4]'}`}
                    onClick={() => setLeftPanelTab('files')}
                  >
                    <FolderOpen className="h-3.5 w-3.5 inline mr-1" />Examples
                  </button>
                  <button
                    className={`flex-1 px-3 py-2 text-xs font-medium ${leftPanelTab === 'exercises' ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808080] hover:text-[#d4d4d4]'}`}
                    onClick={() => setLeftPanelTab('exercises')}
                  >
                    <BookOpen className="h-3.5 w-3.5 inline mr-1" />Exercises
                  </button>
                </div>

                {/* Examples */}
                {leftPanelTab === 'files' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      <div className="text-xs text-[#808080] uppercase tracking-wider mb-2 px-2">AICL Examples</div>
                      {examples.map(ex => (
                        <button
                          key={ex.id}
                          className="w-full flex items-center gap-2 px-2 py-1.5 text-xs rounded hover:bg-[#2d2d30] group text-left"
                          onClick={() => openExample(ex)}
                        >
                          <FileText className="h-3.5 w-3.5 text-[#4ec9b0] flex-shrink-0" />
                          <div className="min-w-0">
                            <div className="truncate text-[#d4d4d4]">{ex.title}</div>
                            <div className="text-[#808080] truncate">{ex.description}</div>
                          </div>
                        </button>
                      ))}

                      <div className="text-xs text-[#808080] uppercase tracking-wider mb-2 mt-4 px-2">Open Files</div>
                      {files.map(f => (
                        <button
                          key={f.id}
                          className={`w-full flex items-center gap-2 px-2 py-1.5 text-xs rounded group text-left ${f.id === activeFileId ? 'bg-[#2d2d30] text-white' : 'hover:bg-[#2d2d30] text-[#d4d4d4]'}`}
                          onClick={() => setActiveFileId(f.id)}
                        >
                          <File className="h-3.5 w-3.5 text-[#4ec9b0] flex-shrink-0" />
                          <span className="truncate">{f.name}</span>
                          {f.modified && <span className="w-1.5 h-1.5 rounded-full bg-[#cd2d48] flex-shrink-0" />}
                        </button>
                      ))}
                    </div>
                  </ScrollArea>
                )}

                {/* Exercises */}
                {leftPanelTab === 'exercises' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      <div className="text-xs text-[#808080] uppercase tracking-wider mb-2 px-2">Progressive Exercises</div>
                      {exercises.map(ex => (
                        <button
                          key={ex.id}
                          className={`w-full flex items-start gap-2 px-2 py-2 text-xs rounded hover:bg-[#2d2d30] text-left ${activeExercise === ex.id ? 'bg-[#2d2d30] border-l-2 border-[#cd2d48]' : ''}`}
                          onClick={() => openExercise(ex)}
                        >
                          <div className="w-5 h-5 rounded-full bg-[#2d2d30] flex items-center justify-center flex-shrink-0 mt-0.5 border border-[#3c3c3c]">
                            <span className="text-[10px] text-[#cd2d48] font-bold">{ex.id}</span>
                          </div>
                          <div className="min-w-0">
                            <div className="text-[#d4d4d4] font-medium">{ex.title}</div>
                            <div className="text-[#808080] line-clamp-2 mt-0.5">{ex.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </div>
              <div className="resize-handle w-1 bg-[#3c3c3c] hover:bg-[#cd2d48] cursor-col-resize flex-shrink-0" />
            </>
          )}

          {/* --- Center: Code Editor --- */}
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            {/* Auto-complete hint */}
            <div className="flex items-center gap-2 px-3 py-1 bg-[#252526] border-b border-[#3c3c3c] flex-shrink-0">
              <span className="text-[10px] text-[#808080]">
                Ctrl+Space: Auto-complete | Tab: Indent | Shift+Tab: Outdent | Enter: Auto-indent
              </span>
              <div className="flex-1" />
              <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs hover:bg-[#2d2d30]" onClick={() => setLeftPanelOpen(!leftPanelOpen)}>
                {leftPanelOpen ? <PanelLeftClose className="h-3.5 w-3.5" /> : <PanelLeftOpen className="h-3.5 w-3.5" />}
              </Button></TooltipTrigger><TooltipContent>Toggle left panel</TooltipContent></Tooltip>
              <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs hover:bg-[#2d2d30]" onClick={() => setRightPanelOpen(!rightPanelOpen)}>
                {rightPanelOpen ? <PanelRightClose className="h-3.5 w-3.5" /> : <PanelRightOpen className="h-3.5 w-3.5" />}
              </Button></TooltipTrigger><TooltipContent>Toggle right panel</TooltipContent></Tooltip>
            </div>

            {/* Editor Area */}
            <div className="flex-1 relative overflow-hidden">
              {/* Line numbers + Highlighted overlay + Textarea */}
              <div className="absolute inset-0 flex">
                {/* Line numbers */}
                <div className="w-12 bg-[#1e1e1e] text-right pr-3 pt-2 select-none overflow-hidden flex-shrink-0">
                  {lineNumbers.map(n => (
                    <div key={n} className="text-[11px] leading-[21px] text-[#4f4f4f] font-mono">{n}</div>
                  ))}
                </div>

                {/* Code area */}
                <div className="flex-1 relative">
                  {/* Syntax highlighted background */}
                  <pre
                    className="absolute inset-0 pt-2 pl-0 pr-4 overflow-auto pointer-events-none editor-textarea whitespace-pre text-[#d4d4d4]"
                    aria-hidden="true"
                    dangerouslySetInnerHTML={{ __html: highlightedCode }}
                    style={{ font: '14px/1.5 var(--font-geist-mono), "Consolas", monospace' }}
                  />

                  {/* Actual textarea */}
                  <textarea
                    ref={textareaRef}
                    className="absolute inset-0 pt-2 pl-0 pr-4 editor-textarea bg-transparent text-transparent caret-[#d4d4d4] resize-none focus:outline-none whitespace-pre overflow-auto"
                    value={activeFile.content}
                    onChange={(e) => updateFileContent(activeFileId, e.target.value)}
                    onKeyDown={handleKeyDown}
                    onKeyUp={handleCursorChange}
                    onClick={handleCursorChange}
                    onScroll={(e) => {
                      const pre = e.currentTarget.previousElementSibling as HTMLElement;
                      if (pre) pre.scrollTop = e.currentTarget.scrollTop;
                      const lineNumContainer = e.currentTarget.parentElement?.previousElementSibling as HTMLElement;
                      if (lineNumContainer) lineNumContainer.scrollTop = e.currentTarget.scrollTop;
                    }}
                    spellCheck={false}
                    autoCapitalize="off"
                    autoComplete="off"
                    autoCorrect="off"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* --- Right Panel --- */}
          {rightPanelOpen && (
            <>
              <div className="resize-handle w-1 bg-[#3c3c3c] hover:bg-[#cd2d48] cursor-col-resize flex-shrink-0" />
              <div className="w-80 bg-[#252526] border-l border-[#3c3c3c] flex flex-col flex-shrink-0 overflow-hidden">
                {/* Right panel tabs */}
                <div className="flex border-b border-[#3c3c3c]">
                  {(['output', 'tree', 'code', 'chat'] as const).map(tab => (
                    <button
                      key={tab}
                      className={`flex-1 px-2 py-1.5 text-[10px] font-medium capitalize ${rightPanelContent === tab ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808080] hover:text-[#d4d4d4]'}`}
                      onClick={() => {
                        setRightPanelContent(tab);
                        if (tab === 'tree') setTreeData('');
                        if (tab === 'chat') setTimeout(() => chatInputRef.current?.focus(), 100);
                      }}
                    >
                      {tab === 'output' && <FileSearch className="h-3 w-3 inline mr-1" />}
                      {tab === 'tree' && <TreePine className="h-3 w-3 inline mr-1" />}
                      {tab === 'code' && <Code2 className="h-3 w-3 inline mr-1" />}
                      {tab === 'chat' && <MessageSquare className="h-3 w-3 inline mr-1" />}
                      {tab}
                    </button>
                  ))}
                </div>

                {/* Output */}
                {rightPanelContent === 'output' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2 font-mono text-xs">
                      {output.map((entry, i) => (
                        <div key={i} className={`py-0.5 ${
                          entry.type === 'success' ? 'text-[#4ec9b0]' :
                          entry.type === 'error' ? 'text-[#f44747]' :
                          entry.type === 'warning' ? 'text-[#dcdcaa]' :
                          entry.type === 'system' ? 'text-[#808080]' :
                          'text-[#d4d4d4]'
                        }`}>
                          <span className="text-[#4f4f4f] mr-2" suppressHydrationWarning>
                            {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                          </span>
                          {entry.type === 'success' && <CheckCircle className="h-3 w-3 inline mr-1" />}
                          {entry.type === 'error' && <XCircle className="h-3 w-3 inline mr-1" />}
                          {entry.type === 'warning' && <AlertTriangle className="h-3 w-3 inline mr-1" />}
                          <span className="whitespace-pre-wrap">{entry.message}</span>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}

                {/* Tree */}
                {rightPanelContent === 'tree' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      <pre className="font-mono text-xs text-[#4ec9b0] whitespace-pre">{treeData || 'Click "Tree" in toolbar to generate'}</pre>
                    </div>
                  </ScrollArea>
                )}

                {/* Generated Code */}
                {rightPanelContent === 'code' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      {compiledCode ? (
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline" className="text-[10px] text-[#4ec9b0] border-[#4ec9b0]">main.py</Badge>
                            <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[10px] hover:bg-[#2d2d30]" onClick={() => { navigator.clipboard.writeText(compiledCode); toast({ title: 'Copied!', description: 'Compiled code copied to clipboard' }); }}>
                              <Copy className="h-3 w-3 mr-1" />Copy
                            </Button>
                          </div>
                          <pre className="font-mono text-[11px] text-[#d4d4d4] whitespace-pre bg-[#1e1e1e] p-2 rounded border border-[#3c3c3c] max-h-[50vh] overflow-auto">{compiledCode}</pre>
                          {testCode && (
                            <div className="mt-3">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className="text-[10px] text-[#dcdcaa] border-[#dcdcaa]">test_main.py</Badge>
                                <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[10px] hover:bg-[#2d2d30]" onClick={() => { navigator.clipboard.writeText(testCode); toast({ title: 'Copied!', description: 'Test code copied to clipboard' }); }}>
                                  <Copy className="h-3 w-3 mr-1" />Copy
                                </Button>
                              </div>
                              <pre className="font-mono text-[11px] text-[#d4d4d4] whitespace-pre bg-[#1e1e1e] p-2 rounded border border-[#3c3c3c] max-h-[50vh] overflow-auto">{testCode}</pre>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs text-[#808080]">Click &quot;Compile&quot; in the toolbar to generate code</div>
                      )}
                    </div>
                  </ScrollArea>
                )}

                {/* AI Chat */}
                {rightPanelContent === 'chat' && (
                  <div className="flex-1 flex flex-col overflow-hidden">
                    <ScrollArea className="flex-1">
                      <div className="p-3 space-y-3">
                        {chatMessages.map((msg, i) => (
                          <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.role === 'assistant' && (
                              <div className="w-6 h-6 rounded-full bg-[#cd2d48] flex items-center justify-center flex-shrink-0 mt-0.5">
                                <Bot className="h-3.5 w-3.5 text-white" />
                              </div>
                            )}
                            <div className={`max-w-[85%] rounded-lg text-xs leading-relaxed ${
                              msg.role === 'user'
                                ? 'bg-[#cd2d48] text-white rounded-br-sm px-3 py-2'
                                : 'bg-[#2d2d30] text-[#d4d4d4] rounded-bl-sm'
                            }`}>
                              {msg.role === 'user' ? (
                                <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                              ) : (
                                <div>
                                  {msg.content && (
                                    <div className="whitespace-pre-wrap break-words px-3 py-2">{msg.content}</div>
                                  )}
                                  {msg.aiclFiles?.map((file, fi) => (
                                    <div key={fi} className="border-t border-[#3c3c3c] mt-1">
                                      <div className="flex items-center gap-2 px-3 py-1.5 bg-[#1e1e1e]">
                                        <FileText className="h-3.5 w-3.5 text-[#4ec9b0]" />
                                        <span className="text-[#4ec9b0] font-mono text-[11px]">{file.filename}</span>
                                      </div>
                                      <pre className="px-3 py-2 text-[11px] font-mono text-[#d4d4d4] whitespace-pre overflow-x-auto max-h-40 bg-[#1e1e1e]">{file.code}</pre>
                                      <div className="flex items-center gap-1.5 px-3 py-2 bg-[#1e1e1e]">
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#4ec9b0] hover:bg-[#3ba890] text-[#1e1e1e]"
                                          onClick={() => chatCreateFile(file.filename, file.code)}
                                        >
                                          <Plus className="h-3 w-3 mr-1" />Create File
                                        </Button>
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#cd2d48] hover:bg-[#a8233b] text-white"
                                          onClick={() => chatCreateAndCompile(file.filename, file.code)}
                                          disabled={isRunning}
                                        >
                                          <Play className="h-3 w-3 mr-1" />Create + Compile
                                        </Button>
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#569cd6] hover:bg-[#4a8bc2] text-white"
                                          onClick={() => chatCreateAndVerify(file.filename, file.code)}
                                          disabled={isRunning}
                                        >
                                          <ShieldCheck className="h-3 w-3 mr-1" />Verify
                                        </Button>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                            {msg.role === 'user' && (
                              <div className="w-6 h-6 rounded-full bg-[#3c3c3c] flex items-center justify-center flex-shrink-0 mt-0.5">
                                <User className="h-3.5 w-3.5 text-[#d4d4d4]" />
                              </div>
                            )}
                          </div>
                        ))}
                        {chatLoading && (
                          <div className="flex gap-2 justify-start">
                            <div className="w-6 h-6 rounded-full bg-[#cd2d48] flex items-center justify-center flex-shrink-0">
                              <Bot className="h-3.5 w-3.5 text-white" />
                            </div>
                            <div className="bg-[#2d2d30] px-3 py-2 rounded-lg rounded-bl-sm">
                              <Loader2 className="h-4 w-4 animate-spin text-[#cd2d48]" />
                            </div>
                          </div>
                        )}
                        <div ref={chatEndRef} />
                      </div>
                    </ScrollArea>
                    <div className="flex items-center gap-2 px-3 py-2 border-t border-[#3c3c3c]">
                      <input
                        ref={chatInputRef}
                        className="flex-1 bg-[#3c3c3c] border border-[#4f4f4f] rounded px-2 py-1.5 text-xs text-[#d4d4d4] focus:outline-none focus:border-[#cd2d48]"
                        placeholder='Try "Describe a todo app in AICL"...'
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); } }}
                        disabled={chatLoading}
                      />
                      <Button
                        size="sm"
                        className="h-7 w-7 p-0 bg-[#cd2d48] hover:bg-[#a8233b]"
                        onClick={sendChatMessage}
                        disabled={chatLoading || !chatInput.trim()}
                      >
                        <Send className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* ======== BOTTOM PANEL ======== */}
        {bottomPanelOpen && (
          <div className="h-52 bg-[#252526] border-t border-[#3c3c3c] flex flex-col flex-shrink-0">
            {/* Bottom panel tabs */}
            <div className="flex items-center border-b border-[#3c3c3c]">
              {(['output', 'repl', 'exercises'] as const).map(tab => (
                <button
                  key={tab}
                  className={`px-3 py-1.5 text-xs font-medium capitalize ${bottomPanelTab === tab ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808080] hover:text-[#d4d4d4]'}`}
                  onClick={() => setBottomPanelTab(tab)}
                >
                  {tab === 'output' && <FileSearch className="h-3 w-3 inline mr-1" />}
                  {tab === 'repl' && <Terminal className="h-3 w-3 inline mr-1" />}
                  {tab === 'exercises' && <BookOpen className="h-3 w-3 inline mr-1" />}
                  {tab}
                </button>
              ))}
              <div className="flex-1" />
              <Button variant="ghost" size="sm" className="h-6 px-2 mr-1 text-xs hover:bg-[#2d2d30]" onClick={() => setBottomPanelOpen(false)}>
                <Minimize2 className="h-3 w-3" />
              </Button>
            </div>

            {/* Output tab */}
            {bottomPanelTab === 'output' && (
              <ScrollArea className="flex-1">
                <div className="p-2 font-mono text-xs">
                  {output.map((entry, i) => (
                    <div key={i} className={`py-0.5 ${
                      entry.type === 'success' ? 'text-[#4ec9b0]' :
                      entry.type === 'error' ? 'text-[#f44747]' :
                      entry.type === 'warning' ? 'text-[#dcdcaa]' :
                      entry.type === 'system' ? 'text-[#808080]' :
                      'text-[#d4d4d4]'
                    }`}>
                      <span className="text-[#4f4f4f] mr-2" suppressHydrationWarning>
                        {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                      </span>
                      {entry.message}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}

            {/* REPL tab */}
            {bottomPanelTab === 'repl' && (
              <div className="flex-1 flex flex-col overflow-hidden">
                <ScrollArea className="flex-1">
                  <div className="p-2 font-mono text-xs">
                    {replHistory.map((entry, i) => (
                      <div key={i} className={`py-0.5 ${
                        entry.type === 'success' ? 'text-[#4ec9b0]' :
                        entry.type === 'error' ? 'text-[#f44747]' :
                        entry.type === 'warning' ? 'text-[#dcdcaa]' :
                        entry.type === 'system' ? 'text-[#808080]' :
                        'text-[#d4d4d4]'
                      }`}>
                        {entry.message}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="flex items-center gap-2 px-2 py-1 border-t border-[#3c3c3c]">
                  <span className="text-[#cd2d48] font-mono text-xs">{'>>>'}</span>
                  <input
                    ref={replInputRef}
                    className="flex-1 bg-transparent text-xs text-[#d4d4d4] font-mono focus:outline-none"
                    placeholder="Type AICL or :help for commands..."
                    value={replInput}
                    onChange={(e) => setReplInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleReplSubmit(); }}
                  />
                </div>
              </div>
            )}

            {/* Exercises tab */}
            {bottomPanelTab === 'exercises' && (
              <ScrollArea className="flex-1">
                <div className="p-3">
                  {activeExercise ? (
                    <div>
                      {(() => {
                        const ex = exercises.find(e => e.id === activeExercise);
                        if (!ex) return <div className="text-xs text-[#808080]">No exercise selected</div>;
                        return (
                          <>
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="outline" className="text-[#cd2d48] border-[#cd2d48] text-xs">Exercise {ex.id}</Badge>
                              <span className="text-sm font-medium text-[#d4d4d4]">{ex.title}</span>
                            </div>
                            <p className="text-xs text-[#808080] mb-3">{ex.description}</p>
                            <div className="flex gap-2">
                              <Button size="sm" className="h-7 text-xs bg-[#cd2d48] hover:bg-[#a8233b]" onClick={checkExercise} disabled={isRunning}>
                                {isRunning ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <Check className="h-3 w-3 mr-1" />}
                                Check
                              </Button>
                              <Button size="sm" variant="outline" className="h-7 text-xs border-[#3c3c3c] hover:bg-[#2d2d30]" onClick={() => setActiveExercise(null)}>
                                Back to list
                              </Button>
                            </div>
                          </>
                        );
                      })()}
                    </div>
                  ) : (
                    <div>
                      <div className="text-xs text-[#808080] mb-3">Select an exercise to start learning AICL:</div>
                      {exercises.map(ex => (
                        <button
                          key={ex.id}
                          className="w-full flex items-start gap-2 px-2 py-2 text-xs rounded hover:bg-[#2d2d30] text-left mb-1"
                          onClick={() => openExercise(ex)}
                        >
                          <div className="w-5 h-5 rounded-full bg-[#2d2d30] flex items-center justify-center flex-shrink-0 mt-0.5 border border-[#3c3c3c]">
                            <span className="text-[10px] text-[#cd2d48] font-bold">{ex.id}</span>
                          </div>
                          <div className="min-w-0">
                            <div className="text-[#d4d4d4] font-medium">{ex.title}</div>
                            <div className="text-[#808080] line-clamp-2 mt-0.5">{ex.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}
          </div>
        )}

        {/* ======== STATUS BAR ======== */}
        <div className="flex items-center justify-between px-3 py-1 bg-[#cd2d48] text-white text-[11px] flex-shrink-0">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              AICL v1.0.0
            </span>
            <span className="flex items-center gap-1">
              <File className="h-3 w-3" />
              {activeFile.name}
              {activeFile.modified && ' (modified)'}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span>Ln {cursorPos.line}, Col {cursorPos.col}</span>
            <span>Target: {targetLang}</span>
            <span>UTF-8</span>
            {isRunning && <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" />Processing...</span>}
            {!bottomPanelOpen && (
              <button className="hover:text-white/80" onClick={() => setBottomPanelOpen(true)}>
                <Maximize2 className="h-3 w-3" />
              </button>
            )}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

// Small helper icon component for code tab
function Code2({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m18 16 4-4-4-4" /><path d="m6 8-4 4 4 4" /><path d="m14.5 4-5 16" />
    </svg>
  );
}
