import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

export type Route =
  | { name: 'landing' }
  | { name: 'how-it-works' }
  | { name: 'signin' }
  | { name: 'workspace' }
  | { name: 'new-analysis' }
  | { name: 'standards' }
  | { name: 'reports' }
  | { name: 'analysis'; analysisId: string; tab?: AnalysisTab }
  | { name: 'standard'; standardId: string };

export type AnalysisTab = 'overview' | 'standards' | 'relationships' | 'gaps' | 'certification' | 'evidence';

interface RouterContextValue {
  route: Route;
  navigate: (route: Route) => void;
}

const RouterContext = createContext<RouterContextValue | null>(null);

export function useRouter() {
  const ctx = useContext(RouterContext);
  if (!ctx) throw new Error('useRouter must be used within RouterProvider');
  return ctx;
}

function parseHash(): Route {
  const hash = window.location.hash.replace(/^#/, '') || '/';
  const parts = hash.split('/').filter(Boolean);

  if (parts.length === 0) return { name: 'landing' };
  if (parts[0] === 'how-it-works') return { name: 'how-it-works' };
  if (parts[0] === 'signin') return { name: 'signin' };
  if (parts[0] === 'workspace') return { name: 'workspace' };
  if (parts[0] === 'new-analysis') return { name: 'new-analysis' };
  if (parts[0] === 'standards') return { name: 'standards' };
  if (parts[0] === 'reports') return { name: 'reports' };
  if (parts[0] === 'analysis' && parts[1]) {
    const tab = (parts[2] as AnalysisTab) || 'overview';
    return { name: 'analysis', analysisId: parts[1], tab };
  }
  if (parts[0] === 'standard' && parts[1]) {
    return { name: 'standard', standardId: parts[1] };
  }
  return { name: 'landing' };
}

function routeToHash(route: Route): string {
  switch (route.name) {
    case 'landing':
      return '#/';
    case 'how-it-works':
      return '#/how-it-works';
    case 'signin':
      return '#/signin';
    case 'workspace':
      return '#/workspace';
    case 'new-analysis':
      return '#/new-analysis';
    case 'standards':
      return '#/standards';
    case 'reports':
      return '#/reports';
    case 'analysis':
      return `#/analysis/${route.analysisId}${route.tab ? `/${route.tab}` : ''}`;
    case 'standard':
      return `#/standard/${route.standardId}`;
  }
}

export function RouterProvider({ children }: { children: ReactNode }) {
  const [route, setRoute] = useState<Route>(() => parseHash());

  useEffect(() => {
    const onHashChange = () => {
      setRoute(parseHash());
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigate = useCallback((newRoute: Route) => {
    window.location.hash = routeToHash(newRoute);
  }, []);

  const value = useMemo(() => ({ route, navigate }), [route, navigate]);

  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}
