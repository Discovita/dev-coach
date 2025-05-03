import { LoginForm } from '@/pages/login/components/login-form';
import { motion } from 'framer-motion';

function Login() {
  return (
    <div className="_Login text-center mb-24">
      <motion.div
        className="m-auto flex justify-center"
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, delay: 0.5 }}
      >
        <div className="flex flex-col items-center">
          <span className="sr-only">Log in to your account</span>
          <h1 className="text-gold-700 text-2xl font-bold tracking-tight sm:text-4xl mb-12">
            Login
          </h1>
        </div>
      </motion.div>
      <motion.div
        key="login-form"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.8 }}
      >
        <LoginForm />
      </motion.div>
    </div>
  );
}

export default Login;
