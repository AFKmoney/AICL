'use client';

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable';
import type { ImperativePanelHandle } from 'react-resizable-panels';
import {
  Play, Shield, FileSearch, Brain, TreePine, Zap, Trash2,
  FileText, FolderOpen, Save, Plus, Search, Replace,
  ChevronRight, ChevronDown, File, X, Check, AlertTriangle,
  Info, XCircle, CheckCircle, Loader2, Terminal, BookOpen,
  Copy, Download, RotateCcw, Maximize2, Minimize2, PanelLeftClose,
  PanelLeftOpen, PanelRightClose, PanelRightOpen,
  Layers, ShieldCheck, Bug, Lightbulb, GitBranch, Gauge,
  MessageSquare, Send, Bot, User, Code2, Wrench, RefreshCw
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
const DEFAULT_FILE = `# AICL - Artificial Intelligence-Centered Language
# Specification-first programming with AX sub-language and Proof of Origin.

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
  const [output, setOutput] = useState<OutputEntry[]>([
    { type: 'system', message: 'AICL Web Editor v5.0 — Cognitive Architecture Ready (SpecEvolver + Autonomous Loop)', timestamp: 0 }
  ]);
  const [replHistory, setReplHistory] = useState<OutputEntry[]>([
    { type: 'system', message: 'AICL Interactive Shell v5.0 — Type AICL statements or commands', timestamp: 0 }
  ]);
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
  interface ChatError {
    operation: string; // 'compile', 'verify', 'audit', etc.
    message: string;
    details?: string[];
  }
  interface ChatMsg {
    role: 'user' | 'assistant';
    content: string;
    aiclFiles?: AICLFileBlock[]; // parsed :::AICL_FILE blocks
    error?: ChatError; // structured error info for display
  }
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([
    { role: 'assistant', content: '__WELCOME_SPLASH__' },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [evolving, setEvolving] = useState(false);
  const [autoFixing, setAutoFixing] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const replInputRef = useRef<HTMLInputElement>(null);
  const findInputRef = useRef<HTMLInputElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  const leftPanelRef = useRef<ImperativePanelHandle>(null);
  const rightPanelRef = useRef<ImperativePanelHandle>(null);
  const bottomPanelRef = useRef<ImperativePanelHandle>(null);

  const activeFile = files.find(f => f.id === activeFileId) || files[0];

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
        // Also show error in chat if it's open
        if (rightPanelContent === 'chat') {
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'compile',
              message: `Compilation of ${activeFile.name} failed`,
              details: data.errors?.length ? data.errors : ['Unknown compilation error. Click "Explain Error" for help.'],
            },
          }]);
        }
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      addOutput('error', `Compile error: ${errMsg}`);
      if (rightPanelContent === 'chat') {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          error: {
            operation: 'compile',
            message: `Compilation of ${activeFile.name} failed — server error`,
            details: [errMsg, 'Check if the server is running and try again.'],
          },
        }]);
      }
    }
    setIsRunning(false);
  }, [activeFile, targetLang, addOutput, rightPanelContent]);

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
      // Show verification errors in chat if it's open and there are failures
      if (rightPanelContent === 'chat' && data.overall !== 'PASS') {
        const failedChecks = (data.checks || []).filter((c: VerifyCheck) => c.status === 'FAIL');
        const warnChecks = (data.checks || []).filter((c: VerifyCheck) => c.status === 'WARN');
        if (failedChecks.length > 0 || warnChecks.length > 0) {
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'verify',
              message: `Verification of ${activeFile.name}: ${data.overall}`,
              details: [
                ...failedChecks.map((c: VerifyCheck) => `FAIL — ${c.name}: ${c.message}${c.details ? '\n  → ' + c.details.join('\n  → ') : ''}`),
                ...warnChecks.map((c: VerifyCheck) => `WARN — ${c.name}: ${c.message}`),
              ],
            },
          }]);
        }
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      addOutput('error', `Verify error: ${errMsg}`);
      if (rightPanelContent === 'chat') {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          error: {
            operation: 'verify',
            message: `Verification of ${activeFile.name} failed — server error`,
            details: [errMsg],
          },
        }]);
      }
    }
    setIsRunning(false);
  }, [activeFile, addOutput, rightPanelContent]);

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
        if (rightPanelContent === 'chat') {
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'audit',
              message: `Audit of ${activeFile.name} failed`,
              details: [data.error, 'Make sure the AICL code has been compiled first, or check the specification for syntax errors.'],
            },
          }]);
        }
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
        // Show audit issues in chat if there are orphans
        if (rightPanelContent === 'chat' && data.orphan_count > 0) {
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'audit',
              message: `Audit of ${activeFile.name}: ${data.orphan_count} orphan artifacts found (No-Orphan Property violated)`,
              details: [
                `Coverage: ${coveragePercent}% — Target: 100%`,
                `Orphan artifacts: ${data.orphan_names?.join(', ') || 'unknown'}`,
                'The No-Orphan Property requires every generated artifact to have a provenance chain to source specification.',
                'Try adding more specific Entity, Behavior, or Validation sections to give the compiler more context.',
              ],
            },
          }]);
        }
      }
      setRightPanelContent('output');
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      addOutput('error', `Audit error: ${errMsg}`);
      if (rightPanelContent === 'chat') {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          error: {
            operation: 'audit',
            message: `Audit of ${activeFile.name} failed — server error`,
            details: [errMsg],
          },
        }]);
      }
    }
    setIsRunning(false);
  }, [activeFile, addOutput, rightPanelContent]);

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

  // --- Auto-Fix (SpecEvolver) ---
  const runAutoFix = useCallback(async (errors?: string[], operation?: string) => {
    setAutoFixing(true);
    setIsRunning(true);
    addOutput('info', `Auto-fixing ${activeFile.name} (SpecEvolver)...`);
    try {
      const res = await fetch('/api/fix-spec', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: activeFile.content,
          filename: activeFile.name,
          errors,
          operation,
        }),
      });
      const data = await res.json();

      if (data.fixed && data.code) {
        // Replace the editor content with the fixed code
        updateFileContent(activeFileId, data.code);
        addOutput('success', `Auto-fix applied! ${data.explanation || 'Specification has been repaired.'}`);
        addOutput('info', `The editor content has been updated with the fixed AICL code.`);
        toast({ title: 'Auto-Fix Applied', description: data.explanation || 'Your AICL code has been fixed automatically.' });
      } else if (data.message && !data.fixed) {
        addOutput('warning', `Auto-fix: ${data.message}`);
        if (data.explanation) addOutput('info', data.explanation);
      } else {
        addOutput('error', 'Auto-fix failed — could not generate a valid fix');
      }
      setRightPanelContent('output');
    } catch (err) {
      addOutput('error', `Auto-fix error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setAutoFixing(false);
    setIsRunning(false);
  }, [activeFile, activeFileId, addOutput, updateFileContent]);

  // --- Evolve (Autonomous Compilation Loop) ---
  const runEvolve = useCallback(async () => {
    setEvolving(true);
    setIsRunning(true);
    addOutput('info', `Starting autonomous compilation loop for ${activeFile.name}...`);
    addOutput('info', `Loop: COMPILE → VERIFY → DIAGNOSE → FIX → RECOMPILE (max 5 iterations)`);
    try {
      const res = await fetch('/api/evolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: activeFile.content, target: targetLang, maxIterations: 5 }),
      });
      const data = await res.json();

      // Log each iteration
      data.iterations?.forEach((iter: { iteration: number; compiled: boolean; verified: string; audit_coverage: number; errors: string[]; fixed: boolean; fix_explanation?: string }) => {
        addOutput('info', `--- Iteration ${iter.iteration} ---`);
        addOutput(iter.compiled ? 'success' : 'error', `Compile: ${iter.compiled ? 'SUCCESS' : 'FAILED'}`);
        addOutput(iter.verified === 'PASS' ? 'success' : iter.verified === 'ERROR' ? 'error' : 'warning', `Verify: ${iter.verified}`);
        if (iter.audit_coverage > 0) {
          addOutput(iter.audit_coverage >= 1.0 ? 'success' : 'warning', `Audit coverage: ${(iter.audit_coverage * 100).toFixed(0)}%`);
        }
        if (iter.errors?.length) {
          iter.errors.forEach((e: string) => addOutput('warning', `  Issue: ${e}`));
        }
        if (iter.fixed) {
          addOutput('info', `Fix applied: ${iter.fix_explanation || 'SpecEvolver repaired the specification'}`);
        }
      });

      if (data.converged) {
        addOutput('success', `CONVERGED! The specification is now valid after ${data.total_iterations} iteration(s).`);
      } else {
        addOutput('warning', `Did not fully converge after ${data.total_iterations} iteration(s). Manual review may be needed.`);
      }

      // Update editor content if source was changed
      if (data.source_changed && data.evolved_source) {
        updateFileContent(activeFileId, data.evolved_source);
        addOutput('info', `Editor content updated with the evolved specification.`);
      }

      // Store compiled code if available
      if (data.main_code) {
        setCompiledCode(data.main_code);
        setTestCode(data.test_code || '');
        setRightPanelContent('code');
      }

      if (data.proof_valid) {
        addOutput('success', 'Proof of Origin: Valid ✓');
      }

      toast({
        title: data.converged ? 'Evolution Converged!' : 'Evolution Complete',
        description: data.converged
          ? `Specification is valid after ${data.total_iterations} iteration(s).`
          : `Improved after ${data.total_iterations} iteration(s), but may need manual review.`,
      });
    } catch (err) {
      addOutput('error', `Evolve error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
    setEvolving(false);
    setIsRunning(false);
  }, [activeFile, activeFileId, targetLang, addOutput, updateFileContent]);

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
          addReplLine('system', '  :fix [errors]   - Auto-fix current file (SpecEvolver)');
          addReplLine('system', '  :evolve [lang]  - Autonomous compilation loop');
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
        case 'fix': {
          addReplLine('info', 'Auto-fixing specification (SpecEvolver)...');
          try {
            const res = await fetch('/api/fix-spec', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content, filename: activeFile.name, errors: args.length > 0 ? args : undefined }),
            });
            const data = await res.json();
            if (data.fixed && data.code) {
              updateFileContent(activeFileId, data.code);
              addReplLine('success', `Auto-fix applied! ${data.explanation || ''}`);
            } else {
              addReplLine('warning', data.message || 'No fix needed or fix unavailable');
            }
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
        case 'evolve': {
          addReplLine('info', `Starting autonomous loop (target: ${args[0] || 'python'})...`);
          try {
            const res = await fetch('/api/evolve', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ source: activeFile.content, target: args[0] || targetLang, maxIterations: 5 }),
            });
            const data = await res.json();
            data.iterations?.forEach((iter: { iteration: number; compiled: boolean; verified: string; audit_coverage: number; fixed: boolean; fix_explanation?: string }) => {
              addReplLine('info', `  Iter ${iter.iteration}: compile=${iter.compiled ? 'OK' : 'FAIL'} verify=${iter.verified} audit=${(iter.audit_coverage * 100).toFixed(0)}%${iter.fixed ? ' [FIXED]' : ''}`);
            });
            addReplLine(data.converged ? 'success' : 'warning', `Evolve: ${data.converged ? 'CONVERGED' : 'not converged'} (${data.total_iterations} iterations)`);
            if (data.source_changed && data.evolved_source) {
              updateFileContent(activeFileId, data.evolved_source);
              addReplLine('info', 'Editor updated with evolved specification');
            }
          } catch (err) {
            addReplLine('error', String(err));
          }
          break;
        }
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
          messages: [...chatMessages, userMessage].map(m => ({ role: m.role, content: m.content === '__WELCOME_SPLASH__' ? 'Hello, I am using the AICL editor.' : m.content })),
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
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: '',
        error: {
          operation: 'chat',
          message: 'Connection to AI assistant failed',
          details: [
            errMsg,
            'The AI service may be temporarily unavailable.',
            'You can still use the editor buttons (Compile, Verify, Audit) manually while the chat is down.',
          ],
        },
      }]);
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
          // Add success message to chat
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: `✓ Compilation of **${filename}** succeeded!\n\n- ${data.stages_completed?.length || 0} stages completed\n- Audit coverage: ${((data.audit_coverage || 0) * 100).toFixed(0)}%\n- Proof of Origin: ${data.proof_valid ? 'Valid ✓' : 'Invalid ✗'}\n\nYou can view the generated code in the **Code** tab.`,
          }]);
        } else {
          const errorDetails = data.errors || ['Unknown compilation error'];
          addOutput('error', 'Compilation failed!');
          errorDetails.forEach((e: string) => addOutput('error', e));
          // Show detailed error in chat
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'compile',
              message: `Compilation of ${filename} failed`,
              details: errorDetails,
            },
          }]);
        }
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : 'Unknown error';
        addOutput('error', `Compile error: ${errMsg}`);
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          error: {
            operation: 'compile',
            message: `Compilation of ${filename} failed — network or server error`,
            details: [errMsg, 'The server may be temporarily unavailable. Try again or verify your AICL code manually.'],
          },
        }]);
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
        // Show verification result in chat
        if (data.overall !== 'PASS') {
          const failedChecks = (data.checks || []).filter((c: VerifyCheck) => c.status === 'FAIL');
          const warnChecks = (data.checks || []).filter((c: VerifyCheck) => c.status === 'WARN');
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            error: {
              operation: 'verify',
              message: `Verification of ${filename}: ${data.overall}`,
              details: [
                ...failedChecks.map((c: VerifyCheck) => `FAIL — ${c.name}: ${c.message}${c.details ? '\n  → ' + c.details.join('\n  → ') : ''}`),
                ...warnChecks.map((c: VerifyCheck) => `WARN — ${c.name}: ${c.message}`),
              ],
            },
          }]);
        } else {
          setChatMessages(prev => [...prev, {
            role: 'assistant',
            content: `✓ Verification of **${filename}** passed! All checks are green.`,
          }]);
        }
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : 'Unknown error';
        addOutput('error', `Verify error: ${errMsg}`);
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: '',
          error: {
            operation: 'verify',
            message: `Verification of ${filename} failed — network or server error`,
            details: [errMsg],
          },
        }]);
      }
      setIsRunning(false);
    }, 200);
  }, [chatCreateFile, addOutput]);

  // Chat action: ask AI to explain an error
  const explainErrorInChat = useCallback(async (errorInfo: ChatError) => {
    setChatMessages(prev => [...prev, {
      role: 'user',
      content: `Explain this error: ${errorInfo.message}${errorInfo.details?.length ? '\n' + errorInfo.details.join('\n') : ''}`,
    }]);
    setChatLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...chatMessages, {
            role: 'user' as const,
            content: `I got this error during ${errorInfo.operation}: ${errorInfo.message}${errorInfo.details?.length ? '\nDetails:\n' + errorInfo.details.join('\n') : ''}\n\nPlease explain what went wrong and how to fix it. Be specific and actionable.`,
          }].map(m => ({ role: m.role, content: m.content === '__WELCOME_SPLASH__' ? 'Hello, I am using the AICL editor.' : m.content })),
          context: activeFile.content,
        }),
      });
      const data = await res.json();
      const rawMessage = data.message || 'Unable to explain the error.';
      setChatMessages(prev => [...prev, { role: 'assistant', content: rawMessage }]);
    } catch {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I cannot connect to the AI right now to explain this error. However, common fixes include:\n\n- Make sure your AICL code has **Goal**, **Layer**, and **Validation** sections\n- Check that all keywords are spelled correctly\n- Ensure Entity/Behavior sections have proper Input/Output/Action structure\n- Risk and Recovery should always be paired',
      }]);
    }
    setChatLoading(false);
  }, [chatMessages, activeFile.content]);

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
      <div className="h-screen flex flex-col bg-[#1a1a2e] text-[#d4d4d4] overflow-hidden">
        {/* ======== TOOLBAR ======== */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-[#1e1e36] to-[#252540] border-b border-[#3c3c50] flex-shrink-0 panel-depth">
          {/* Left: Logo + File ops */}
          <div className="flex items-center gap-2 mr-3">
            <div className="flex items-center gap-2 px-2 py-0.5 rounded-md bg-[#cd2d48]/10 border border-[#cd2d48]/20">
              <div className="w-6 h-6 rounded-md bg-[#cd2d48] flex items-center justify-center shadow-lg shadow-[#cd2d48]/20">
                <span className="text-white text-xs font-black tracking-tight">A</span>
              </div>
              <span className="text-sm font-bold text-[#cd2d48] tracking-wide">AICL</span>
              <span className="text-[10px] text-[#cd2d48]/60 font-medium">v5.0</span>
            </div>
            <div className="w-px h-5 bg-[#3c3c50]" />
          </div>

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={newFile}><Plus className="h-3.5 w-3.5 mr-1.5" />New</Button></TooltipTrigger><TooltipContent>New File</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={loadFile}><FolderOpen className="h-3.5 w-3.5 mr-1.5" />Open</Button></TooltipTrigger><TooltipContent>Open File</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={saveFile}><Save className="h-3.5 w-3.5 mr-1.5" />Save</Button></TooltipTrigger><TooltipContent>Save (Ctrl+S)</TooltipContent></Tooltip>

          <div className="w-px h-5 bg-[#3c3c50] mx-1" />

          {/* Target language selector */}
          <Select value={targetLang} onValueChange={setTargetLang}>
            <SelectTrigger className="h-7 w-[110px] text-xs bg-[#2d2d3d] border-[#3c3c50] rounded-md">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e1e36] border-[#3c3c50]">
              <SelectItem value="python">Python</SelectItem>
              <SelectItem value="rust">Rust</SelectItem>
              <SelectItem value="javascript">JavaScript</SelectItem>
              <SelectItem value="go">Go</SelectItem>
            </SelectContent>
          </Select>

          <div className="w-px h-5 bg-[#3c3c50] mx-1" />

          {/* AICL Actions */}
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-3 text-xs hover:bg-[#4ec9b0]/10 rounded-md text-[#4ec9b0] compile-btn font-semibold transition-all" onClick={runCompile} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <Play className="h-3.5 w-3.5 mr-1.5" />}Compile</Button></TooltipTrigger><TooltipContent>Compile AICL → Code</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#569cd6]/10 rounded-md text-[#569cd6] transition-colors" onClick={runVerify} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <ShieldCheck className="h-3.5 w-3.5 mr-1.5" />}Verify</Button></TooltipTrigger><TooltipContent>Verify specification quality</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#dcdcaa]/10 rounded-md text-[#dcdcaa] transition-colors" onClick={runAudit} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <FileSearch className="h-3.5 w-3.5 mr-1.5" />}Audit</Button></TooltipTrigger><TooltipContent>Audit compilation provenance</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#c586c0]/10 rounded-md text-[#c586c0] transition-colors" onClick={runExplain} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <Brain className="h-3.5 w-3.5 mr-1.5" />}Explain</Button></TooltipTrigger><TooltipContent>Explain compilation provenance</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#6a9955]/10 rounded-md text-[#6a9955] transition-colors" onClick={runTree} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <TreePine className="h-3.5 w-3.5 mr-1.5" />}Tree</Button></TooltipTrigger><TooltipContent>Architecture tree</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#ce9178]/10 rounded-md text-[#ce9178] transition-colors" onClick={runOptimize} disabled={isRunning}>{isRunning ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <Zap className="h-3.5 w-3.5 mr-1.5" />}Optimize</Button></TooltipTrigger><TooltipContent>Optimize architecture</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-3 text-xs hover:bg-[#f97316]/10 rounded-md text-[#f97316] font-semibold transition-all animate-compile-glow" onClick={runEvolve} disabled={isRunning}>{evolving ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5 mr-1.5" />}Evolve</Button></TooltipTrigger><TooltipContent>Autonomous compilation loop (COMPILE → VERIFY → FIX → RECOMPILE)</TooltipContent></Tooltip>

          <div className="w-px h-5 bg-[#3c3c50] mx-1" />

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#cd2d48]/10 rounded-md text-[#cd2d48] transition-colors animate-pulse-glow" onClick={() => { rightPanelRef.current?.expand(); setRightPanelContent('chat'); setTimeout(() => chatInputRef.current?.focus(), 100); }}><MessageSquare className="h-3.5 w-3.5 mr-1.5" />AI Chat</Button></TooltipTrigger><TooltipContent>Open AI Assistant chat</TooltipContent></Tooltip>

          <div className="w-px h-5 bg-[#3c3c50] mx-1" />

          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={clearOutput}><Trash2 className="h-3.5 w-3.5 mr-1.5" />Clear</Button></TooltipTrigger><TooltipContent>Clear output</TooltipContent></Tooltip>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Right: Search */}
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={() => { setFindOpen(!findOpen); setTimeout(() => findInputRef.current?.focus(), 50); }}><Search className="h-3.5 w-3.5 mr-1.5" />Find</Button></TooltipTrigger><TooltipContent>Find & Replace (Ctrl+F)</TooltipContent></Tooltip>
        </div>

        {/* ======== FILE TABS ======== */}
        <div className="flex items-center bg-[#1e1e36] border-b border-[#3c3c50] flex-shrink-0 overflow-x-auto">
          {files.map(file => (
            <div
              key={file.id}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs cursor-pointer border-r border-[#3c3c50] group min-w-0 tab-transition ${
                file.id === activeFileId ? 'bg-[#1a1a2e] text-white border-t-2 border-t-[#cd2d48]' : 'bg-[#252540] text-[#808090] hover:bg-[#2d2d3d]'
              }`}
              onClick={() => setActiveFileId(file.id)}
            >
              <File className="h-3 w-3 text-[#4ec9b0] flex-shrink-0" />
              <span className="truncate max-w-[120px]">{file.name}</span>
              {file.modified && <span className="w-2 h-2 rounded-full bg-[#cd2d48] flex-shrink-0 shadow-sm shadow-[#cd2d48]/30" />}
              <button
                className="ml-1 opacity-0 group-hover:opacity-100 hover:text-white flex-shrink-0 transition-opacity"
                onClick={(e) => { e.stopPropagation(); closeFile(file.id); }}
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
          <button
            className="px-2 py-1.5 text-[#808090] hover:text-white hover:bg-[#2d2d3d] text-xs transition-colors"
            onClick={newFile}
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* ======== FIND/REPLACE BAR ======== */}
        {findOpen && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#1e1e36] border-b border-[#3c3c50] flex-shrink-0">
            <div className="flex items-center gap-1 flex-1">
              <Search className="h-3.5 w-3.5 text-[#808090]" />
              <input
                ref={findInputRef}
                className="bg-[#2d2d3d] border border-[#3c3c50] rounded-md px-2 py-1 text-xs text-[#d4d4d4] w-48 focus:outline-none focus:border-[#cd2d48] transition-colors"
                placeholder="Find..."
                value={findText}
                onChange={(e) => setFindText(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleFindNext(); if (e.key === 'Escape') setFindOpen(false); }}
              />
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs hover:bg-[#2d2d3d]">Next</Button>
            </div>
            <div className="flex items-center gap-1 flex-1">
              <Replace className="h-3.5 w-3.5 text-[#808090]" />
              <input
                className="bg-[#2d2d3d] border border-[#3c3c50] rounded-md px-2 py-1 text-xs text-[#d4d4d4] w-48 focus:outline-none focus:border-[#cd2d48] transition-colors"
                placeholder="Replace..."
                value={replaceText}
                onChange={(e) => setReplaceText(e.target.value)}
              />
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs hover:bg-[#2d2d3d]" onClick={handleReplaceAll}>Replace All</Button>
            </div>
            <Button variant="ghost" size="sm" className="h-6 px-2 hover:bg-[#2d2d3d]" onClick={() => setFindOpen(false)}>
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        )}

        {/* ======== MAIN CONTENT ======== */}
        <ResizablePanelGroup direction="vertical" className="flex-1 overflow-hidden">
          <ResizablePanel defaultSize={75} minSize={30}>
            <ResizablePanelGroup direction="horizontal" className="h-full">
              {/* --- Left Panel --- */}
              <ResizablePanel
                ref={leftPanelRef}
                defaultSize={18}
                minSize={10}
                maxSize={35}
                collapsible
                collapsedSize={0}
                onCollapse={() => setLeftPanelOpen(false)}
                onExpand={() => setLeftPanelOpen(true)}
              >
                <div className="h-full bg-[#1e1e36] flex flex-col overflow-hidden panel-depth">
                {/* Cognitive Vision Banner */}
                <div className="welcome-gradient border-b border-[#3c3c50] p-3">
                  <div className="flex items-center mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-[#cd2d48]">Cognitive Vision</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] font-mono">
                    <span className="px-1.5 py-0.5 rounded bg-[#4ec9b0]/15 text-[#4ec9b0] font-semibold">Architecture</span>
                    <span className="text-[#808090] flow-arrow">→</span>
                    <span className="px-1.5 py-0.5 rounded bg-[#cd2d48]/15 text-[#cd2d48] font-semibold">AICL</span>
                    <span className="text-[#808090] flow-arrow flow-arrow-delay-1">→</span>
                    <span className="px-1.5 py-0.5 rounded bg-[#c586c0]/15 text-[#c586c0] font-semibold">AI</span>
                    <span className="text-[#808090] flow-arrow flow-arrow-delay-2">→</span>
                    <span className="px-1.5 py-0.5 rounded bg-[#569cd6]/15 text-[#569cd6] font-semibold">Code</span>
                  </div>
                  <p className="text-[9px] text-[#808090] mt-2 leading-relaxed">The architecture is the real program. Code is the byproduct.</p>
                </div>

                {/* Panel Tabs */}
                <div className="flex border-b border-[#3c3c50]">
                  <button
                    className={`flex-1 px-3 py-2 text-xs font-medium tab-transition ${leftPanelTab === 'files' ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808090] hover:text-[#d4d4d4]'}`}
                    onClick={() => setLeftPanelTab('files')}
                  >
                    <FolderOpen className="h-3.5 w-3.5 inline mr-1" />Examples
                  </button>
                  <button
                    className={`flex-1 px-3 py-2 text-xs font-medium tab-transition ${leftPanelTab === 'exercises' ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808090] hover:text-[#d4d4d4]'}`}
                    onClick={() => setLeftPanelTab('exercises')}
                  >
                    <BookOpen className="h-3.5 w-3.5 inline mr-1" />Exercises
                  </button>
                </div>

                {/* Examples */}
                {leftPanelTab === 'files' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      <div className="text-xs text-[#808090] uppercase tracking-wider mb-2 px-2 font-semibold">AICL Examples</div>
                      {examples.map(ex => (
                        <button
                          key={ex.id}
                          className="w-full flex items-center gap-2 px-2 py-1.5 text-xs rounded-md hover:bg-[#2d2d3d] group text-left transition-colors"
                          onClick={() => openExample(ex)}
                        >
                          <FileText className="h-3.5 w-3.5 text-[#4ec9b0] flex-shrink-0" />
                          <div className="min-w-0">
                            <div className="truncate text-[#d4d4d4]">{ex.title}</div>
                            <div className="text-[#808090] truncate">{ex.description}</div>
                          </div>
                        </button>
                      ))}

                      <div className="text-xs text-[#808090] uppercase tracking-wider mb-2 mt-4 px-2 font-semibold">Open Files</div>
                      {files.map(f => (
                        <button
                          key={f.id}
                          className={`w-full flex items-center gap-2 px-2 py-1.5 text-xs rounded-md group text-left transition-colors ${f.id === activeFileId ? 'bg-[#2d2d3d] text-white border-l-2 border-l-[#cd2d48]' : 'hover:bg-[#2d2d3d] text-[#d4d4d4]'}`}
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
                      <div className="text-xs text-[#808090] uppercase tracking-wider mb-2 px-2 font-semibold">Progressive Exercises</div>
                      {exercises.map(ex => (
                        <button
                          key={ex.id}
                          className={`w-full flex items-start gap-2 px-2 py-2 text-xs rounded-md hover:bg-[#2d2d3d] text-left transition-colors ${activeExercise === ex.id ? 'bg-[#2d2d3d] border-l-2 border-[#cd2d48]' : ''}`}
                          onClick={() => openExercise(ex)}
                        >
                          <div className="w-5 h-5 rounded-full bg-[#2d2d3d] flex items-center justify-center flex-shrink-0 mt-0.5 border border-[#3c3c50]">
                            <span className="text-[10px] text-[#cd2d48] font-bold">{ex.id}</span>
                          </div>
                          <div className="min-w-0">
                            <div className="text-[#d4d4d4] font-medium">{ex.title}</div>
                            <div className="text-[#808090] line-clamp-2 mt-0.5">{ex.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </ScrollArea>
                )}
                </div>
              </ResizablePanel>

              <ResizableHandle withHandle className="bg-[#3c3c50] hover:bg-[#cd2d48]/60 data-[resize-handle-active]:bg-[#cd2d48]" />

              {/* --- Center: Code Editor --- */}
              <ResizablePanel defaultSize={52} minSize={30}>
                <div className="h-full flex flex-col overflow-hidden min-w-0">
            {/* Auto-complete hint */}
            <div className="flex items-center gap-2 px-3 py-1 bg-[#1e1e36] border-b border-[#3c3c50] flex-shrink-0">
              <span className="text-[10px] text-[#808090]">
                Ctrl+Space: Auto-complete | Tab: Indent | Shift+Tab: Outdent | Enter: Auto-indent
              </span>
              <div className="flex-1" />
              <span className="text-[10px] text-[#4ec9b0]/60 font-mono">{activeFile.content.split('\n').length} lines</span>
              <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs hover:bg-[#2d2d3d] transition-colors" onClick={() => { if (leftPanelOpen) leftPanelRef.current?.collapse(); else leftPanelRef.current?.expand(); }}>
                {leftPanelOpen ? <PanelLeftClose className="h-3.5 w-3.5" /> : <PanelLeftOpen className="h-3.5 w-3.5" />}
              </Button></TooltipTrigger><TooltipContent>Toggle left panel</TooltipContent></Tooltip>
              <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs hover:bg-[#2d2d3d] transition-colors" onClick={() => { if (rightPanelOpen) rightPanelRef.current?.collapse(); else rightPanelRef.current?.expand(); }}>
                {rightPanelOpen ? <PanelRightClose className="h-3.5 w-3.5" /> : <PanelRightOpen className="h-3.5 w-3.5" />}
              </Button></TooltipTrigger><TooltipContent>Toggle right panel</TooltipContent></Tooltip>
            </div>

            {/* Editor Area */}
            <div className="flex-1 relative overflow-hidden">
              {/* Line numbers + Highlighted overlay + Textarea */}
              <div className="absolute inset-0 flex">
                {/* Line numbers */}
                <div className="w-14 bg-[#16162a] text-right pr-4 pt-2 select-none overflow-hidden flex-shrink-0 border-r border-[#2a2a40]">
                  {lineNumbers.map(n => (
                    <div key={n} className={`text-[11px] leading-[21px] font-mono ${n === cursorPos.line ? 'text-[#cd2d48] font-semibold' : 'text-[#4f4f60]'}`}>{n}</div>
                  ))}
                </div>

                {/* Code area */}
                <div className="flex-1 relative">
                  {/* Syntax highlighted background */}
                  <pre
                    className="absolute inset-0 pt-2 pl-2 pr-4 overflow-auto pointer-events-none editor-textarea whitespace-pre text-[#d4d4d4]"
                    aria-hidden="true"
                    dangerouslySetInnerHTML={{ __html: highlightedCode }}
                    style={{ font: '14px/1.5 var(--font-geist-mono), "Consolas", monospace' }}
                  />

                  {/* Actual textarea */}
                  <textarea
                    ref={textareaRef}
                    className="absolute inset-0 pt-2 pl-2 pr-4 editor-textarea bg-transparent text-transparent caret-[#d4d4d4] resize-none focus:outline-none whitespace-pre overflow-auto"
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
              </ResizablePanel>

              <ResizableHandle withHandle className="bg-[#3c3c50] hover:bg-[#cd2d48]/60 data-[resize-handle-active]:bg-[#cd2d48]" />

              {/* --- Right Panel --- */}
              <ResizablePanel
                ref={rightPanelRef}
                defaultSize={30}
                minSize={15}
                maxSize={50}
                collapsible
                collapsedSize={0}
                onCollapse={() => setRightPanelOpen(false)}
                onExpand={() => setRightPanelOpen(true)}
              >
                <div className={`h-full flex flex-col overflow-hidden panel-depth ${rightPanelContent === 'chat' ? 'chat-panel-bg' : 'bg-[#1e1e36]'}`}>
                {/* Right panel tabs */}
                <div className="flex border-b border-[#3c3c50] bg-[#1e1e36]">
                  {(['output', 'tree', 'code', 'chat'] as const).map(tab => (
                    <button
                      key={tab}
                      className={`flex-1 px-2 py-1.5 text-[10px] font-medium capitalize tab-transition ${rightPanelContent === tab ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808090] hover:text-[#d4d4d4]'}`}
                      onClick={() => {
                        setRightPanelContent(tab);
                        if (tab === 'tree') setTreeData('');
                        if (tab === 'chat') setTimeout(() => chatInputRef.current?.focus(), 100);
                      }}
                    >
                      {tab === 'output' && <FileSearch className="h-3 w-3 inline mr-1" />}
                      {tab === 'tree' && <TreePine className="h-3 w-3 inline mr-1" />}
                      {tab === 'code' && <Code2 className="h-3 w-3 inline mr-1" />}
                      {tab === 'chat' && <><MessageSquare className="h-3 w-3 inline mr-1" /><span className="inline-block w-1.5 h-1.5 rounded-full bg-[#4ec9b0] animate-cognitive-pulse ml-0.5" /></>}
                      {tab}
                    </button>
                  ))}
                </div>

                {/* Output */}
                {rightPanelContent === 'output' && (
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      {/* Copy All button */}
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] text-[#808090] uppercase tracking-wider font-semibold">Output</span>
                        <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[10px] text-[#808090] hover:text-white hover:bg-[#2d2d3d] transition-colors" onClick={() => { navigator.clipboard.writeText(output.map(e => e.message).join('\n')); toast({ title: 'Copied!', description: 'All output copied to clipboard' }); }}>
                          <Copy className="h-3 w-3 mr-1" />Copy All
                        </Button>
                      </div>
                      <div className="font-mono text-xs space-y-0.5">
                        {output.map((entry, i) => (
                          <div key={i} className={`py-0.5 rounded px-1.5 ${
                            entry.type === 'success' ? 'text-[#4ec9b0] success-entry' :
                            entry.type === 'error' ? 'text-[#f44747] error-entry bg-[#f44747]/5' :
                            entry.type === 'warning' ? 'text-[#dcdcaa]' :
                            entry.type === 'system' ? 'text-[#808090]' :
                            'text-[#d4d4d4]'
                          }`}>
                            <span className="text-[#4f4f60] mr-2" suppressHydrationWarning>
                              {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                            </span>
                            {entry.type === 'success' && <CheckCircle className="h-3 w-3 inline mr-1" />}
                            {entry.type === 'error' && <XCircle className="h-3.5 w-3.5 inline mr-1" />}
                            {entry.type === 'warning' && <AlertTriangle className="h-3 w-3 inline mr-1" />}
                            {entry.type === 'info' && <Info className="h-3 w-3 inline mr-1 text-[#569cd6]" />}
                            <span className={`whitespace-pre-wrap ${entry.type === 'success' ? 'font-semibold' : ''}`}>{entry.message}</span>
                          </div>
                        ))}
                      </div>
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
                            <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[10px] hover:bg-[#2d2d3d] transition-colors" onClick={() => { navigator.clipboard.writeText(compiledCode); toast({ title: 'Copied!', description: 'Compiled code copied to clipboard' }); }}>
                              <Copy className="h-3 w-3 mr-1" />Copy
                            </Button>
                          </div>
                          <pre className="font-mono text-[11px] text-[#d4d4d4] whitespace-pre bg-[#16162a] p-2 rounded-md border border-[#3c3c50] max-h-[50vh] overflow-auto">{compiledCode}</pre>
                          {testCode && (
                            <div className="mt-3">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className="text-[10px] text-[#dcdcaa] border-[#dcdcaa]">test_main.py</Badge>
                                <Button variant="ghost" size="sm" className="h-5 px-1.5 text-[10px] hover:bg-[#2d2d3d] transition-colors" onClick={() => { navigator.clipboard.writeText(testCode); toast({ title: 'Copied!', description: 'Test code copied to clipboard' }); }}>
                                  <Copy className="h-3 w-3 mr-1" />Copy
                                </Button>
                              </div>
                              <pre className="font-mono text-[11px] text-[#d4d4d4] whitespace-pre bg-[#16162a] p-2 rounded-md border border-[#3c3c50] max-h-[50vh] overflow-auto">{testCode}</pre>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs text-[#808090]">Click &quot;Compile&quot; in the toolbar to generate code</div>
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
                          <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                            {msg.role === 'assistant' && (
                              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#cd2d48] to-[#8b1a2d] flex items-center justify-center flex-shrink-0 mt-0.5 shadow-lg shadow-[#cd2d48]/20">
                                <Bot className="h-3.5 w-3.5 text-white" />
                              </div>
                            )}
                            <div className={`max-w-[85%] rounded-xl text-xs leading-relaxed ${
                              msg.role === 'user'
                                ? 'bg-[#cd2d48] text-white rounded-br-sm px-3 py-2 shadow-lg shadow-[#cd2d48]/10'
                                : 'bg-[#2d2d3d] text-[#d4d4d4] rounded-bl-sm'
                            }`}>
                              {msg.role === 'user' ? (
                                <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                              ) : (
                                <div>
                                  {msg.content === '__WELCOME_SPLASH__' ? (
                                    /* Welcome Splash Screen */
                                    <div className="px-3 py-2">
                                      <div className="flex items-center gap-2 mb-3">
                                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#cd2d48] to-[#8b1a2d] flex items-center justify-center shadow-lg shadow-[#cd2d48]/30">
                                          <span className="text-white text-sm font-black">A</span>
                                        </div>
                                        <div>
                                          <div className="text-[#cd2d48] font-bold text-sm">AICL v5.0</div>
                                          <div className="text-[#808090] text-[10px]">Cognitive Architecture Language</div>
                                        </div>
                                      </div>
                                      <div className="bg-[#1a1a2e] rounded-lg p-3 mb-3 border border-[#3c3c50]">
                                        <p className="text-[#d4d4d4] text-[11px] leading-relaxed italic">
                                          AICL is not a programming language. It is a <span className="text-[#cd2d48] font-semibold">cognitive representation language</span> designed for the learning, reasoning, and autonomous evolution of AI systems.
                                        </p>
                                        <p className="text-[#808090] text-[10px] leading-relaxed mt-2">
                                          The generated code is a byproduct. The architecture is the real program.
                                        </p>
                                      </div>
                                      <div className="flex items-center gap-1 text-[10px] font-mono mb-3">
                                        <span className="px-1.5 py-0.5 rounded bg-[#4ec9b0]/15 text-[#4ec9b0] font-semibold">Architecture</span>
                                        <span className="text-[#808090]">→</span>
                                        <span className="px-1.5 py-0.5 rounded bg-[#cd2d48]/15 text-[#cd2d48] font-semibold">AICL</span>
                                        <span className="text-[#808090]">→</span>
                                        <span className="px-1.5 py-0.5 rounded bg-[#c586c0]/15 text-[#c586c0] font-semibold">AI reasons</span>
                                        <span className="text-[#808090]">→</span>
                                        <span className="px-1.5 py-0.5 rounded bg-[#569cd6]/15 text-[#569cd6] font-semibold">Code</span>
                                      </div>
                                      <div className="text-[10px] text-[#808090] space-y-1">
                                        <div className="flex items-center gap-1.5">
                                          <span className="w-1 h-1 rounded-full bg-[#4ec9b0]" />
                                          <span>Describe architectures, not implementations</span>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                          <span className="w-1 h-1 rounded-full bg-[#cd2d48]" />
                                          <span>No-Orphan Property ensures every artifact has provenance</span>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                          <span className="w-1 h-1 rounded-full bg-[#c586c0]" />
                                          <span>Proof of Origin validates compilation decisions</span>
                                        </div>
                                      </div>
                                      <div className="mt-3 pt-2 border-t border-[#3c3c50]">
                                        <p className="text-[10px] text-[#808090]">Try asking:</p>
                                        <p className="text-[11px] text-[#cd2d48] mt-1">&quot;Describe a todo app in AICL&quot;</p>
                                        <p className="text-[11px] text-[#4ec9b0]">&quot;Write a chat server specification&quot;</p>
                                      </div>
                                    </div>
                                  ) : msg.content && (
                                    <div className="whitespace-pre-wrap break-words px-3 py-2">{msg.content}</div>
                                  )}
                                  {msg.aiclFiles?.map((file, fi) => (
                                    <div key={fi} className="border-t border-[#3c3c50] mt-1 rounded-b-xl overflow-hidden">
                                      <div className="flex items-center gap-2 px-3 py-1.5 bg-[#1a1a2e]">
                                        <FileText className="h-3.5 w-3.5 text-[#4ec9b0]" />
                                        <span className="text-[#4ec9b0] font-mono text-[11px]">{file.filename}</span>
                                      </div>
                                      <pre className="px-3 py-2 text-[11px] font-mono text-[#d4d4d4] whitespace-pre overflow-x-auto max-h-40 bg-[#1a1a2e]">{file.code}</pre>
                                      <div className="flex items-center gap-1.5 px-3 py-2 bg-[#1a1a2e]">
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#4ec9b0] hover:bg-[#3ba890] text-[#1a1a2e] font-semibold rounded-md transition-colors"
                                          onClick={() => chatCreateFile(file.filename, file.code)}
                                        >
                                          <Plus className="h-3 w-3 mr-1" />Create File
                                        </Button>
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#cd2d48] hover:bg-[#a8233b] text-white font-semibold rounded-md transition-colors"
                                          onClick={() => chatCreateAndCompile(file.filename, file.code)}
                                          disabled={isRunning}
                                        >
                                          <Play className="h-3 w-3 mr-1" />Create + Compile
                                        </Button>
                                        <Button
                                          size="sm"
                                          className="h-6 text-[10px] px-2 bg-[#569cd6] hover:bg-[#4a8bc2] text-white font-semibold rounded-md transition-colors"
                                          onClick={() => chatCreateAndVerify(file.filename, file.code)}
                                          disabled={isRunning}
                                        >
                                          <ShieldCheck className="h-3 w-3 mr-1" />Verify
                                        </Button>
                                      </div>
                                    </div>
                                  ))}
                                  {msg.error && (
                                    <div className="border-t border-[#5c1a1a] mt-1 bg-[#2a1015] rounded-b-xl overflow-hidden error-entry">
                                      <div className="flex items-center gap-2 px-3 py-2">
                                        <XCircle className="h-5 w-5 text-[#f87171] flex-shrink-0" />
                                        <span className="text-[#f87171] font-bold text-xs">{msg.error.message}</span>
                                      </div>
                                      {msg.error.details && msg.error.details.length > 0 && (
                                        <div className="px-3 pb-2 space-y-1">
                                          {msg.error.details.map((d, di) => (
                                            <div key={di} className="flex gap-2 text-[11px]">
                                              <span className="text-[#f87171] flex-shrink-0">→</span>
                                              <span className="text-[#fca5a5] whitespace-pre-wrap break-words">{d}</span>
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                      <div className="flex items-center gap-1.5 px-3 py-2 border-t border-[#5c1a1a]">
                                        <Button
                                          size="sm"
                                          className="h-7 text-[10px] px-3 bg-[#f87171] hover:bg-[#ef4444] text-[#1a1a2e] font-semibold rounded-md transition-colors"
                                          onClick={() => explainErrorInChat(msg.error!)}
                                          disabled={chatLoading}
                                        >
                                          <Bug className="h-3 w-3 mr-1" />Explain Error
                                        </Button>
                                        <Button
                                          size="sm"
                                          className="h-7 text-[10px] px-3 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-md transition-colors"
                                          onClick={() => runAutoFix(msg.error?.details || msg.error ? [msg.error!.message, ...(msg.error!.details || [])] : undefined, msg.error?.operation)}
                                          disabled={autoFixing || isRunning}
                                        >
                                          {autoFixing ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <Wrench className="h-3 w-3 mr-1" />}Auto-Fix
                                        </Button>
                                        {msg.error.operation === 'compile' && (
                                          <Button
                                            size="sm"
                                            className="h-7 text-[10px] px-2 bg-[#4ec9b0] hover:bg-[#3ba890] text-[#1a1a2e] font-semibold rounded-md transition-colors"
                                            onClick={() => chatCreateAndVerify(
                                              activeFile.name,
                                              activeFile.content
                                            )}
                                            disabled={isRunning}
                                          >
                                            <ShieldCheck className="h-3 w-3 mr-1" />Verify
                                          </Button>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                            {msg.role === 'user' && (
                              <div className="w-7 h-7 rounded-full bg-[#2d2d3d] flex items-center justify-center flex-shrink-0 mt-0.5 border border-[#3c3c50]">
                                <User className="h-3.5 w-3.5 text-[#d4d4d4]" />
                              </div>
                            )}
                          </div>
                        ))}
                        {chatLoading && (
                          <div className="flex gap-2 justify-start animate-fade-in">
                            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#cd2d48] to-[#8b1a2d] flex items-center justify-center flex-shrink-0">
                              <Bot className="h-3.5 w-3.5 text-white" />
                            </div>
                            <div className="bg-[#2d2d3d] px-4 py-2.5 rounded-xl rounded-bl-sm">
                              <div className="flex items-center gap-2">
                                <Loader2 className="h-4 w-4 animate-spin text-[#cd2d48]" />
                                <span className="text-[#808090] text-[11px]">Cognitive agent reasoning...</span>
                                <span className="w-1.5 h-1.5 rounded-full bg-[#4ec9b0] animate-cognitive-pulse" />
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={chatEndRef} />
                      </div>
                    </ScrollArea>
                    <div className="flex items-center gap-2 px-3 py-2.5 border-t border-[#3c3c50] bg-[#1e1e36]">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#4ec9b0] animate-cognitive-pulse" />
                        <span className="text-[9px] text-[#4ec9b0]/60">COGNITIVE</span>
                      </div>
                      <input
                        ref={chatInputRef}
                        className="flex-1 bg-[#2d2d3d] border border-[#3c3c50] rounded-lg px-3 py-2 text-xs text-[#d4d4d4] focus:outline-none focus:border-[#cd2d48] transition-colors"
                        placeholder='Try "Describe a todo app in AICL"...'
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); } }}
                        disabled={chatLoading}
                      />
                      <Button
                        size="sm"
                        className="h-8 w-8 p-0 bg-[#cd2d48] hover:bg-[#a8233b] rounded-lg transition-colors shadow-lg shadow-[#cd2d48]/20"
                        onClick={sendChatMessage}
                        disabled={chatLoading || !chatInput.trim()}
                      >
                        <Send className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                )}
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>

          <ResizableHandle withHandle className="bg-[#3c3c50] hover:bg-[#cd2d48]/60 data-[resize-handle-active]:bg-[#cd2d48]" />

          {/* ======== BOTTOM PANEL ======== */}
          <ResizablePanel
            ref={bottomPanelRef}
            defaultSize={25}
            minSize={10}
            maxSize={50}
            collapsible
            collapsedSize={0}
            onCollapse={() => setBottomPanelOpen(false)}
            onExpand={() => setBottomPanelOpen(true)}
          >
            <div className="h-full bg-[#1e1e36] border-t border-[#3c3c50] flex flex-col panel-depth">
            {/* Bottom panel tabs */}
            <div className="flex items-center border-b border-[#3c3c50] bg-[#1e1e36]">
              {(['output', 'repl', 'exercises'] as const).map(tab => (
                <button
                  key={tab}
                  className={`px-3 py-1.5 text-xs font-medium capitalize tab-transition ${bottomPanelTab === tab ? 'text-[#cd2d48] border-b-2 border-[#cd2d48]' : 'text-[#808090] hover:text-[#d4d4d4]'}`}
                  onClick={() => setBottomPanelTab(tab)}
                >
                  {tab === 'output' && <FileSearch className="h-3 w-3 inline mr-1" />}
                  {tab === 'repl' && <Terminal className="h-3 w-3 inline mr-1" />}
                  {tab === 'exercises' && <BookOpen className="h-3 w-3 inline mr-1" />}
                  {tab}
                </button>
              ))}
              <div className="flex-1" />
              <Button variant="ghost" size="sm" className="h-6 px-2 mr-1 text-xs hover:bg-[#2d2d3d] transition-colors" onClick={() => bottomPanelRef.current?.collapse()}>
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
                      entry.type === 'system' ? 'text-[#808090]' :
                      'text-[#d4d4d4]'
                    }`}>
                      <span className="text-[#4f4f60] mr-2" suppressHydrationWarning>
                        {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                      </span>
                      {entry.type === 'success' && <CheckCircle className="h-3 w-3 inline mr-1" />}
                      {entry.type === 'error' && <XCircle className="h-3 w-3 inline mr-1" />}
                      {entry.type === 'warning' && <AlertTriangle className="h-3 w-3 inline mr-1" />}
                      {entry.type === 'info' && <Info className="h-3 w-3 inline mr-1 text-[#569cd6]" />}
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
                        entry.type === 'system' ? 'text-[#808090]' :
                        'text-[#d4d4d4]'
                      }`}>
                        {entry.message}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="flex items-center gap-2 px-2 py-1 border-t border-[#3c3c50]">
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
                        if (!ex) return <div className="text-xs text-[#808090]">No exercise selected</div>;
                        return (
                          <>
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="outline" className="text-[#cd2d48] border-[#cd2d48] text-xs">Exercise {ex.id}</Badge>
                              <span className="text-sm font-medium text-[#d4d4d4]">{ex.title}</span>
                            </div>
                            <p className="text-xs text-[#808090] mb-3">{ex.description}</p>
                            <div className="flex gap-2">
                              <Button size="sm" className="h-7 text-xs bg-[#cd2d48] hover:bg-[#a8233b] rounded-md transition-colors" onClick={checkExercise} disabled={isRunning}>
                                {isRunning ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <Check className="h-3 w-3 mr-1" />}
                                Check
                              </Button>
                              <Button size="sm" variant="outline" className="h-7 text-xs border-[#3c3c50] hover:bg-[#2d2d3d] rounded-md transition-colors" onClick={() => setActiveExercise(null)}>
                                Back to list
                              </Button>
                            </div>
                          </>
                        );
                      })()}
                    </div>
                  ) : (
                    <div>
                      <div className="text-xs text-[#808090] mb-3">Select an exercise to start learning AICL:</div>
                      {exercises.map(ex => (
                        <button
                          key={ex.id}
                          className="w-full flex items-start gap-2 px-2 py-2 text-xs rounded-md hover:bg-[#2d2d3d] text-left mb-1 transition-colors"
                          onClick={() => openExercise(ex)}
                        >
                          <div className="w-5 h-5 rounded-full bg-[#2d2d3d] flex items-center justify-center flex-shrink-0 mt-0.5 border border-[#3c3c50]">
                            <span className="text-[10px] text-[#cd2d48] font-bold">{ex.id}</span>
                          </div>
                          <div className="min-w-0">
                            <div className="text-[#d4d4d4] font-medium">{ex.title}</div>
                            <div className="text-[#808090] line-clamp-2 mt-0.5">{ex.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>

        {/* ======== STATUS BAR ======== */}
        <div className="flex items-center justify-between px-3 py-1 bg-gradient-to-r from-[#cd2d48] via-[#b02540] to-[#cd2d48] text-white text-[11px] flex-shrink-0 shadow-[0_-2px_8px_rgba(205,45,72,0.15)]">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 font-semibold">
              <Layers className="h-3 w-3" />
              AICL v5.0
            </span>
            <span className="flex items-center gap-1 text-white/80">
              <File className="h-3 w-3" />
              {activeFile.name}
              {activeFile.modified && ' (modified)'}
            </span>
            <span className="text-white/60 text-[10px] hidden sm:inline">Architecture {'>'} Implementation</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#4ec9b0] animate-cognitive-pulse" />
              AI Connected
            </span>
            <span>Ln {cursorPos.line}, Col {cursorPos.col}</span>
            <span>Target: {targetLang}</span>
            <span>UTF-8</span>
            {isRunning && <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" />Processing...</span>}
            {!bottomPanelOpen && (
              <button className="hover:text-white/80 transition-colors" onClick={() => bottomPanelRef.current?.expand()}>
                <Maximize2 className="h-3 w-3" />
              </button>
            )}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

