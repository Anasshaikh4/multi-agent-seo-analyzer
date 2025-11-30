import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  FileSearch, 
  FileText, 
  Zap, 
  Search, 
  FileOutput,
  CheckCircle2,
  Loader2,
  Clock,
  Globe
} from 'lucide-react';
import { AgentStatus, UserDetails } from '../types';

interface AnalyzingScreenProps {
  userDetails: UserDetails;
  agents: AgentStatus[];
  currentAgent: string | null;
}

const agentIcons: Record<string, React.ReactNode> = {
  security: <Shield className="w-5 h-5" />,
  onpage: <FileSearch className="w-5 h-5" />,
  content: <FileText className="w-5 h-5" />,
  performance: <Zap className="w-5 h-5" />,
  indexability: <Search className="w-5 h-5" />,
  report: <FileOutput className="w-5 h-5" />,
};

const agentLabels: Record<string, string> = {
  security: 'Security',
  onpage: 'On-Page',
  content: 'Content',
  performance: 'Speed',
  indexability: 'Index',
  report: 'Report',
};

export function AnalyzingScreen({ userDetails, agents }: AnalyzingScreenProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const dotsTimer = setInterval(() => {
      setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);
    return () => clearInterval(dotsTimer);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const completedCount = agents.filter(a => a.status === 'completed').length;
  const progress = (completedCount / agents.length) * 100;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-4xl text-center"
      >
        {/* Spinning Globe */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring' }}
          className="w-16 h-16 mx-auto mb-6 relative"
        >
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-blue-500/30"
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          />
          <motion.div
            className="absolute inset-1 rounded-full border-4 border-purple-500/30"
            animate={{ rotate: -360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <Globe className="w-6 h-6 text-blue-400" />
          </div>
        </motion.div>

        {/* Title */}
        <h2 className="text-xl font-bold text-white mb-1">
          Analyzing {userDetails.websiteUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')}
        </h2>
        <p className="text-gray-400 text-sm mb-6">
          AI agents are working{dots}
        </p>

        {/* Progress Bar */}
        <div className="max-w-md mx-auto mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-500">Progress</span>
            <span className="text-xs text-gray-400">{Math.round(progress)}%</span>
          </div>
          <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Horizontal Agents Grid */}
        <div className="grid grid-cols-6 gap-3 mb-8">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative p-4 rounded-xl transition-all duration-300 ${
                agent.status === 'running'
                  ? 'bg-blue-500/10 border-2 border-blue-500/50 shadow-lg shadow-blue-500/20'
                  : agent.status === 'completed'
                  ? 'bg-green-500/10 border-2 border-green-500/50'
                  : 'bg-dark-800/50 border-2 border-dark-600'
              }`}
            >
              {/* Status indicator dot */}
              {agent.status === 'running' && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
              
              {/* Icon */}
              <div
                className={`w-10 h-10 mx-auto mb-2 rounded-lg flex items-center justify-center ${
                  agent.status === 'running'
                    ? 'bg-blue-500/20 text-blue-400'
                    : agent.status === 'completed'
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-dark-700 text-gray-500'
                }`}
              >
                {agent.status === 'running' ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <Loader2 className="w-5 h-5" />
                  </motion.div>
                ) : agent.status === 'completed' ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  agentIcons[agent.name] || <Clock className="w-5 h-5" />
                )}
              </div>

              {/* Label */}
              <p className={`text-xs font-medium ${
                agent.status === 'running'
                  ? 'text-blue-400'
                  : agent.status === 'completed'
                  ? 'text-green-400'
                  : 'text-gray-500'
              }`}>
                {agentLabels[agent.name] || agent.name}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Timer */}
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          <span>Elapsed: <span className="text-gray-300 font-medium">{formatTime(elapsedTime)}</span></span>
        </div>
      </motion.div>
    </div>
  );
}
