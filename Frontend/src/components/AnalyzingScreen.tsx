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
  Globe,
  Lightbulb,
  TrendingUp,
  BarChart3,
  Target,
  Rocket,
  Brain
} from 'lucide-react';
import { AgentStatus, UserDetails } from '../types';
import { useTheme } from '../context/ThemeContext';

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

// SEO Facts for floating cards
const seoFacts = [
  { icon: TrendingUp, text: "53% of website traffic comes from organic search", color: "blue" },
  { icon: Zap, text: "Page speed impacts 70% of buying decisions", color: "yellow" },
  { icon: Target, text: "75% of users never scroll past page 1", color: "red" },
  { icon: BarChart3, text: "SEO leads have 14.6% close rate", color: "green" },
  { icon: Brain, text: "6 AI agents analyze 50+ ranking factors", color: "purple" },
  { icon: Rocket, text: "Mobile-first indexing is now default", color: "orange" },
  { icon: Lightbulb, text: "Quality content increases dwell time 3x", color: "cyan" },
  { icon: Shield, text: "HTTPS sites rank higher on Google", color: "emerald" },
];

const colorClasses: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-300', icon: 'text-blue-400' },
  yellow: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-300', icon: 'text-yellow-400' },
  red: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-300', icon: 'text-red-400' },
  green: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-300', icon: 'text-green-400' },
  purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-300', icon: 'text-purple-400' },
  orange: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-300', icon: 'text-orange-400' },
  cyan: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-300', icon: 'text-cyan-400' },
  emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-300', icon: 'text-emerald-400' },
};

// Floating card component
function FloatingFactCard({ fact, index }: { fact: typeof seoFacts[0]; index: number }) {
  const colors = colorClasses[fact.color];
  const Icon = fact.icon;
  
  // Random positions and animations for each card
  const positions = [
    { x: '3%', y: '8%' },
    { x: '78%', y: '12%' },
    { x: '5%', y: '72%' },
    { x: '75%', y: '68%' },
    { x: '2%', y: '40%' },
    { x: '80%', y: '42%' },
    { x: '8%', y: '22%' },
    { x: '72%', y: '82%' },
  ];
  
  const pos = positions[index % positions.length];
  
  return (
    <motion.div
      className={`absolute max-w-[240px] px-4 py-3 rounded-2xl ${colors.bg} border ${colors.border} backdrop-blur-sm shadow-lg cursor-default transition-opacity duration-300 hover:!opacity-90`}
      style={{ left: pos.x, top: pos.y }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ 
        opacity: [0.25, 0.45, 0.25],
        y: [0, -20, 0],
        rotate: [0, 3, -3, 0],
      }}
      whileHover={{
        scale: 1.05,
        opacity: 1,
        rotate: 0,
        transition: { duration: 0.2 }
      }}
      transition={{ 
        duration: 4 + index * 0.5,
        repeat: Infinity,
        delay: index * 0.8,
        ease: "easeInOut"
      }}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-6 h-6 ${colors.icon} flex-shrink-0 mt-0.5`} />
        <p className={`text-sm ${colors.text} leading-snug font-medium`}>{fact.text}</p>
      </div>
    </motion.div>
  );
}

export function AnalyzingScreen({ userDetails, agents }: AnalyzingScreenProps) {
  const { isDark } = useTheme();
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
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative overflow-hidden">
      {/* Floating SEO Fact Cards */}
      {/* Floating SEO Fact Cards */}
      <div className="absolute inset-0">
        {seoFacts.map((fact, index) => (
          <FloatingFactCard key={index} fact={fact} index={index} />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-4xl text-center relative z-10 pointer-events-none"
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
        <h2 className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Analyzing {userDetails.websiteUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')}
        </h2>
        <p className={`text-sm mb-6 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          AI agents are working{dots}
        </p>

        {/* Progress Bar */}
        <div className="max-w-md mx-auto mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Progress</span>
            <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{Math.round(progress)}%</span>
          </div>
          <div className={`h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-gray-200'}`}>
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
                  : isDark ? 'bg-dark-800/50 border-2 border-dark-600' : 'bg-white/50 border-2 border-gray-200'
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
                    : isDark ? 'bg-dark-700 text-gray-500' : 'bg-gray-100 text-gray-400'
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
                  : isDark ? 'text-gray-500' : 'text-gray-400'
              }`}>
                {agentLabels[agent.name] || agent.name}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Timer */}
        <div className={`flex items-center justify-center gap-2 text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
          <Clock className="w-4 h-4" />
          <span>Elapsed: <span className={`font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{formatTime(elapsedTime)}</span></span>
        </div>
      </motion.div>
    </div>
  );
}
