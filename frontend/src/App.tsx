import { RouterProvider, useRouter } from '@/router';
import { ThemeProvider } from '@/theme/ThemeContext';
import { LandingPage } from '@/pages/LandingPage';
import { HowItWorksPage } from '@/pages/HowItWorksPage';
import { SignInPage } from '@/pages/SignInPage';
import { WorkspacePage } from '@/pages/WorkspacePage';
import { NewAnalysisPage } from '@/pages/NewAnalysisPage';
import { StandardsPage } from '@/pages/StandardsPage';
import { ReportsPage } from '@/pages/ReportsPage';
import { AnalysisPage } from '@/pages/AnalysisPage';
import { StandardDetailPage } from '@/pages/StandardDetailPage';

function AppRouter() {
  const { route } = useRouter();

  switch (route.name) {
    case 'landing':
      return <LandingPage />;
    case 'how-it-works':
      return <HowItWorksPage />;
    case 'signin':
      return <SignInPage />;
    case 'workspace':
      return <WorkspacePage />;
    case 'new-analysis':
      return <NewAnalysisPage />;
    case 'standards':
      return <StandardsPage />;
    case 'reports':
      return <ReportsPage />;
    case 'analysis':
      return <AnalysisPage analysisId={route.analysisId} tab={route.tab || 'overview'} />;
    case 'standard':
      return <StandardDetailPage standardId={route.standardId} />;
    default:
      return <LandingPage />;
  }
}

function App() {
  return (
    <ThemeProvider>
      <RouterProvider>
        <AppRouter />
      </RouterProvider>
    </ThemeProvider>
  );
}

export default App;


