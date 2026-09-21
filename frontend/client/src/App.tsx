import { Route, Switch } from "wouter";
import AppShell from "./components/layout/AppShell";
import Dashboard from "./pages/Dashboard";
import RegulatoryChanges from "./pages/RegulatoryChanges";
import RegulatoryChangeDetail from "./pages/RegulatoryChangeDetail";
import { DocumentDetail, Documents } from "./pages/Documents";
import Sources from "./pages/Sources";
import BusinessProfile from "./pages/BusinessProfile";
import Review from "./pages/Review";
import { Settings, SystemStatus } from "./pages/UtilityPages";

function NotFound() {
  return <div className="mx-auto max-w-xl px-6 py-24 text-center"><div className="label-caps">404 · Not found</div><h1 className="mt-3 font-display text-3xl font-semibold text-[#234b5c]">This record is not in the workspace</h1><p className="mt-3 text-sm leading-6 text-[#82939a]">The route may be valid in the live API but is not available in the demo dataset.</p><a href="/" className="mt-6 inline-flex rounded-xl bg-[#245f68] px-4 py-2.5 text-xs font-semibold text-white">Return to dashboard</a></div>;
}

function Router() {
  return <Switch>
    <Route path="/" component={Dashboard} />
    <Route path="/changes" component={RegulatoryChanges} />
    <Route path="/changes/:id" component={RegulatoryChangeDetail} />
    <Route path="/documents" component={Documents} />
    <Route path="/documents/:id">{(params) => <DocumentDetail id={params.id} />}</Route>
    <Route path="/sources" component={Sources} />
    <Route path="/business-profile" component={BusinessProfile} />
    <Route path="/review" component={Review} />
    <Route path="/settings" component={Settings} />
    <Route path="/system-status" component={SystemStatus} />
    <Route component={NotFound} />
  </Switch>;
}

export default function App() {
  return <AppShell><Router /></AppShell>;
}
