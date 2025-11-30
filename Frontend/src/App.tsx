import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WelcomeScreen } from './components/WelcomeScreen';
import { FormScreen } from './components/FormScreen';
import { AnalyzingScreen } from './components/AnalyzingScreen';
import { ResultsScreen } from './components/ResultsScreen';
import { ParticleBackground } from './components/ParticleBackground';
import { ThemeToggle } from './components/ThemeToggle';
import { useTheme } from './context/ThemeContext';
import { AppStep, UserDetails, AgentStatus } from './types';
import { startAnalysis, getAnalysisProgress, downloadPdfReport } from './api';

// Agent configuration
const INITIAL_AGENTS: AgentStatus[] = [
  { name: 'security', status: 'pending' },
  { name: 'onpage', status: 'pending' },
  { name: 'content', status: 'pending' },
  { name: 'performance', status: 'pending' },
  { name: 'indexability', status: 'pending' },
  { name: 'report', status: 'pending' },
];

function App() {
  const [currentStep, setCurrentStep] = useState<AppStep>('welcome');
  const [userDetails, setUserDetails] = useState<UserDetails | null>(null);
  const [agents, setAgents] = useState<AgentStatus[]>(INITIAL_AGENTS);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [requestId, setRequestId] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleStart = useCallback(() => {
    setCurrentStep('form');
  }, []);

  const handleFormSubmit = useCallback(async (details: UserDetails) => {
    setUserDetails(details);
    setCurrentStep('analyzing');
    setAgents(INITIAL_AGENTS.map(a => ({ ...a, status: 'pending' as const })));

    try {
      // Start the actual analysis via API
      const response = await startAnalysis(details.websiteUrl, details.name, details.email);
      const reqId = response.request_id;
      setRequestId(reqId);

      // Poll for progress updates
      pollingRef.current = setInterval(async () => {
        try {
          const progress = await getAnalysisProgress(reqId);
          
          // Update agent statuses from backend
          if (progress.agents && progress.agents.length > 0) {
            setAgents(progress.agents);
          }
          setCurrentAgent(progress.current_agent || null);

          // Check if completed
          if (progress.status === 'completed') {
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            
            // Wait 1.5 seconds so user can see all agents completed
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            setCurrentStep('results');
          } else if (progress.status === 'error') {
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            console.error('Analysis failed');
            // Could show error state here
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 1000); // Poll every second
    } catch (err) {
      console.error('Failed to start analysis:', err);
      // Could show error state here
    }
  }, []);

  const handleNewAnalysis = useCallback(() => {
    setCurrentStep('form');
    setAgents(INITIAL_AGENTS);
    setCurrentAgent(null);
    setRequestId(null);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const handleBackToHome = useCallback(() => {
    setCurrentStep('welcome');
    setUserDetails(null);
    setAgents(INITIAL_AGENTS);
    setCurrentAgent(null);
    setRequestId(null);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const handleDownloadPdf = useCallback(async () => {
    if (!requestId) return;
    
    setIsDownloading(true);
    try {
      // Always try to download PDF from backend first
      const blob = await downloadPdfReport(requestId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `seo-report-${userDetails?.websiteUrl.replace(/[^a-z0-9]/gi, '-')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('PDF download failed. Please try again.');
    }
    setIsDownloading(false);
  }, [requestId, userDetails]);

  const { isDark } = useTheme();

  return (
    <div className={`min-h-screen relative overflow-hidden transition-colors duration-500 ${
      isDark ? 'bg-dark-900' : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50'
    }`}>
      <ThemeToggle />
      <ParticleBackground />
      
      <div className="relative z-10">
        <AnimatePresence mode="wait">
          {currentStep === 'welcome' && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <WelcomeScreen onStart={handleStart} />
            </motion.div>
          )}

          {currentStep === 'form' && (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.5 }}
            >
              <FormScreen 
                onSubmit={handleFormSubmit} 
                onBack={handleBackToHome}
                initialValues={userDetails}
              />
            </motion.div>
          )}

          {currentStep === 'analyzing' && userDetails && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.5 }}
            >
              <AnalyzingScreen 
                userDetails={userDetails}
                agents={agents}
                currentAgent={currentAgent}
              />
            </motion.div>
          )}

          {currentStep === 'results' && userDetails && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.5 }}
            >
              <ResultsScreen 
                userDetails={userDetails}
                onNewAnalysis={handleNewAnalysis}
                onDownloadPdf={handleDownloadPdf}
                isDownloading={isDownloading}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
