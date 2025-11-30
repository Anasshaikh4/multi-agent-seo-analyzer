import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Globe, Mail, User, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { UserDetails } from '../types';

interface FormScreenProps {
  onSubmit: (details: UserDetails) => void;
  onBack: () => void;
  initialValues?: UserDetails | null;
}

interface FormErrors {
  name?: string;
  email?: string;
  websiteUrl?: string;
}

export function FormScreen({ onSubmit, onBack, initialValues }: FormScreenProps) {
  const [name, setName] = useState(initialValues?.name || '');
  const [email, setEmail] = useState(initialValues?.email || '');
  const [websiteUrl, setWebsiteUrl] = useState(initialValues?.websiteUrl || '');
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validation functions
  const validateName = (value: string): string | undefined => {
    if (!value.trim()) return 'Name is required';
    if (value.trim().length < 2) return 'Name must be at least 2 characters';
    if (value.trim().length > 50) return 'Name must be less than 50 characters';
    return undefined;
  };

  const validateEmail = (value: string): string | undefined => {
    if (!value.trim()) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Please enter a valid email address';
    return undefined;
  };

  const validateUrl = (value: string): string | undefined => {
    if (!value.trim()) return 'Website URL is required';
    try {
      let urlToTest = value.trim();
      if (!urlToTest.startsWith('http://') && !urlToTest.startsWith('https://')) {
        urlToTest = 'https://' + urlToTest;
      }
      const url = new URL(urlToTest);
      if (!url.hostname.includes('.')) {
        return 'Please enter a valid domain';
      }
    } catch {
      return 'Please enter a valid URL';
    }
    return undefined;
  };

  const validateField = useCallback((field: string, value: string) => {
    let error: string | undefined;
    switch (field) {
      case 'name':
        error = validateName(value);
        break;
      case 'email':
        error = validateEmail(value);
        break;
      case 'websiteUrl':
        error = validateUrl(value);
        break;
    }
    setErrors(prev => ({ ...prev, [field]: error }));
    return error;
  }, []);

  const handleBlur = (field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    validateField(field, field === 'name' ? name : field === 'email' ? email : websiteUrl);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const nameError = validateField('name', name);
    const emailError = validateField('email', email);
    const urlError = validateField('websiteUrl', websiteUrl);
    
    setTouched({ name: true, email: true, websiteUrl: true });

    if (nameError || emailError || urlError) {
      return;
    }

    setIsSubmitting(true);

    // Format URL
    let formattedUrl = websiteUrl.trim();
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = 'https://' + formattedUrl;
    }

    // Simulate a brief delay for UX
    await new Promise(resolve => setTimeout(resolve, 500));

    onSubmit({
      name: name.trim(),
      email: email.trim(),
      websiteUrl: formattedUrl,
    });
  };

  const isValid = !validateName(name) && !validateEmail(email) && !validateUrl(websiteUrl);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        {/* Back Button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={onBack}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span>Back to Home</span>
        </motion.button>

        {/* Form Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-2xl p-8 gradient-border"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center"
            >
              <Globe className="w-8 h-8 text-white" />
            </motion.div>
            <h2 className="text-2xl font-bold text-white mb-2">Enter Your Details</h2>
            <p className="text-gray-400">We'll analyze your website and send you a detailed report</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                Your Name
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (touched.name) validateField('name', e.target.value);
                  }}
                  onBlur={() => handleBlur('name')}
                  placeholder="John Doe"
                  maxLength={50}
                  className={`w-full pl-12 pr-12 py-3 bg-dark-800 border rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 transition-all ${
                    touched.name && errors.name 
                      ? 'border-red-500 focus:ring-red-500' 
                      : touched.name && !errors.name 
                        ? 'border-green-500' 
                        : 'border-dark-600'
                  }`}
                />
                {touched.name && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    {errors.name ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                )}
              </div>
              {touched.name && errors.name && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-red-400 flex items-center gap-1"
                >
                  <AlertCircle className="w-4 h-4" />
                  {errors.name}
                </motion.p>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (touched.email) validateField('email', e.target.value);
                  }}
                  onBlur={() => handleBlur('email')}
                  placeholder="john@example.com"
                  className={`w-full pl-12 pr-12 py-3 bg-dark-800 border rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 transition-all ${
                    touched.email && errors.email 
                      ? 'border-red-500 focus:ring-red-500' 
                      : touched.email && !errors.email 
                        ? 'border-green-500' 
                        : 'border-dark-600'
                  }`}
                />
                {touched.email && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    {errors.email ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                )}
              </div>
              {touched.email && errors.email && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-red-400 flex items-center gap-1"
                >
                  <AlertCircle className="w-4 h-4" />
                  {errors.email}
                </motion.p>
              )}
            </div>

            {/* URL Field */}
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
                Website URL
              </label>
              <div className="relative">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  id="url"
                  value={websiteUrl}
                  onChange={(e) => {
                    setWebsiteUrl(e.target.value);
                    if (touched.websiteUrl) validateField('websiteUrl', e.target.value);
                  }}
                  onBlur={() => handleBlur('websiteUrl')}
                  placeholder="example.com or https://example.com"
                  className={`w-full pl-12 pr-12 py-3 bg-dark-800 border rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 transition-all ${
                    touched.websiteUrl && errors.websiteUrl 
                      ? 'border-red-500 focus:ring-red-500' 
                      : touched.websiteUrl && !errors.websiteUrl 
                        ? 'border-green-500' 
                        : 'border-dark-600'
                  }`}
                />
                {touched.websiteUrl && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    {errors.websiteUrl ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                )}
              </div>
              {touched.websiteUrl && errors.websiteUrl && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-red-400 flex items-center gap-1"
                >
                  <AlertCircle className="w-4 h-4" />
                  {errors.websiteUrl}
                </motion.p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                Enter your website URL with or without https://
              </p>
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={!isValid || isSubmitting}
              whileHover={{ scale: isValid && !isSubmitting ? 1.02 : 1 }}
              whileTap={{ scale: isValid && !isSubmitting ? 0.98 : 1 }}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-3 ${
                isValid && !isSubmitting
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-blue-500/25'
                  : 'bg-dark-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting Analysis...
                </>
              ) : (
                <>
                  Start SEO Analysis
                  <span>→</span>
                </>
              )}
            </motion.button>
          </form>

          {/* Privacy Note */}
          <p className="mt-6 text-center text-xs text-gray-500">
            Your data is secure. We only use it to generate your SEO report.
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
