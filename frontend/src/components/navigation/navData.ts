import {
  LayoutDashboard,
  Box,
  Zap,
  Thermometer,
  ShieldAlert,
  TrendingDown,
  FlaskConical,
  Database,
  History,
  Terminal,
} from "lucide-react";
import React from "react";

export interface NavItem {
  id: string;
  title: string;
  path: string;
  category: "Explore" | "Intelligence" | "Experiments" | "Operations";
  description: string;
  badge?: string;
  badgeColor?: "cyan" | "amber" | "coral" | "mint" | "blue";
  iconName: string;
  icon: React.ComponentType<{ className?: string }>;
  hotkey?: string;
}

export interface NavGroup {
  name: "Explore" | "Intelligence" | "Experiments" | "Operations";
  description: string;
  items: NavItem[];
}

export const NAV_ITEMS: NavItem[] = [
  // 1. Explore
  {
    id: "command-centre",
    title: "Command Centre",
    path: "/command-centre",
    category: "Explore",
    description: "Mission control overview, real-time telemetry feed, and 3D twin status.",
    badge: "Control Room",
    badgeColor: "cyan",
    iconName: "LayoutDashboard",
    icon: LayoutDashboard,
    hotkey: "1",
  },
  {
    id: "twin-lab",
    title: "Twin Lab",
    path: "/twin-lab",
    category: "Explore",
    description: "Fullscreen interactive 3D digital twin, exploded cell view, and thermal mesh.",
    badge: "Interactive 3D",
    badgeColor: "cyan",
    iconName: "Box",
    icon: Box,
    hotkey: "2",
  },

  // 2. Intelligence
  {
    id: "electrical-lab",
    title: "Electrical Lab",
    path: "/electrical-lab",
    category: "Intelligence",
    description: "2RC ECM impedance analytics, terminal voltage residual, and EKF innovation gate.",
    badge: "Physics EKF",
    badgeColor: "cyan",
    iconName: "Zap",
    icon: Zap,
    hotkey: "3",
  },
  {
    id: "thermal-observatory",
    title: "Thermal Observatory",
    path: "/thermal-observatory",
    category: "Intelligence",
    description: "Core vs surface temperature gradient, heat generation, and Two-Node thermal observer.",
    badge: "Two-Node Model",
    badgeColor: "amber",
    iconName: "Thermometer",
    icon: Thermometer,
    hotkey: "4",
  },
  {
    id: "anomaly-observatory",
    title: "Anomaly Observatory",
    path: "/anomaly-observatory",
    category: "Intelligence",
    description: "Dual-channel CUSUM detection, fault isolation matrix, and precursor alerting.",
    badge: "Advisory Precursor",
    badgeColor: "coral",
    iconName: "ShieldAlert",
    icon: ShieldAlert,
    hotkey: "5",
  },
  {
    id: "battery-health",
    title: "Battery Health",
    path: "/battery-health",
    category: "Intelligence",
    description: "Hybrid Ridge + XGBoost SoH proxy estimator, capacity fade trajectory, and RUL.",
    badge: "Hybrid ML",
    badgeColor: "mint",
    iconName: "TrendingDown",
    icon: TrendingDown,
    hotkey: "6",
  },

  // 3. Experiments
  {
    id: "experiment-studio",
    title: "Experiment Studio",
    path: "/experiment-studio",
    category: "Experiments",
    description: "NASA B0005/B0006/B0018 replay harness and software fault injection suite.",
    badge: "NASA Replay",
    badgeColor: "amber",
    iconName: "FlaskConical",
    icon: FlaskConical,
    hotkey: "7",
  },
  {
    id: "data-explorer",
    title: "Data Explorer",
    path: "/data-explorer",
    category: "Experiments",
    description: "High-rate telemetry querying, multi-channel correlation analysis, and CSV export.",
    badge: "Raw Query",
    badgeColor: "blue",
    iconName: "Database",
    icon: Database,
    hotkey: "8",
  },

  // 4. Operations
  {
    id: "event-timeline",
    title: "Event Timeline",
    path: "/event-timeline",
    category: "Operations",
    description: "Structured audit log of state changes, CUSUM alarms, and advisory events.",
    badge: "Audit Trail",
    badgeColor: "blue",
    iconName: "History",
    icon: History,
    hotkey: "9",
  },
  {
    id: "system-console",
    title: "System Console",
    path: "/system-console",
    category: "Operations",
    description: "Firmware safety status, serial connection monitor, relay heartbeat, and AST guards.",
    badge: "Firmware Safety",
    badgeColor: "mint",
    iconName: "Terminal",
    icon: Terminal,
    hotkey: "0",
  },
];

export const NAV_GROUPS: NavGroup[] = [
  {
    name: "Explore",
    description: "Spatial 3D visualization and high-level control room views.",
    items: NAV_ITEMS.filter((i) => i.category === "Explore"),
  },
  {
    name: "Intelligence",
    description: "Physics observers, EKF state estimation, and machine learning models.",
    items: NAV_ITEMS.filter((i) => i.category === "Intelligence"),
  },
  {
    name: "Experiments",
    description: "NASA telemetry replay, fault injection, and dataset exploration.",
    items: NAV_ITEMS.filter((i) => i.category === "Experiments"),
  },
  {
    name: "Operations",
    description: "Audit trails, firmware safety boundaries, and system health.",
    items: NAV_ITEMS.filter((i) => i.category === "Operations"),
  },
];

