import { createBrowserRouter, Navigate } from "react-router-dom";
import { App } from "./App";
import {
  CommandCentrePage,
  TwinLabPage,
  ElectricalLabPage,
  ThermalObservatoryPage,
  AnomalyObservatoryPage,
  BatteryHealthPage,
  ExperimentStudioPage,
  DataExplorerPage,
  EventTimelinePage,
  SystemConsolePage,
} from "../pages";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <Navigate to="/command-centre" replace />,
      },
      {
        path: "command-centre",
        element: <CommandCentrePage />,
      },
      {
        path: "twin-lab",
        element: <TwinLabPage />,
      },
      {
        path: "electrical-lab",
        element: <ElectricalLabPage />,
      },
      {
        path: "thermal-observatory",
        element: <ThermalObservatoryPage />,
      },
      {
        path: "anomaly-observatory",
        element: <AnomalyObservatoryPage />,
      },
      {
        path: "battery-health",
        element: <BatteryHealthPage />,
      },
      {
        path: "experiment-studio",
        element: <ExperimentStudioPage />,
      },
      {
        path: "data-explorer",
        element: <DataExplorerPage />,
      },
      {
        path: "event-timeline",
        element: <EventTimelinePage />,
      },
      {
        path: "system-console",
        element: <SystemConsolePage />,
      },
      {
        path: "*",
        element: <Navigate to="/command-centre" replace />,
      },
    ],
  },
]);
