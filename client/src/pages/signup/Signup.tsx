import { SignupForm } from "@/pages/signup/components/signup-form";
import { motion } from "framer-motion";

function Signup() {
  return (
    <div className="_SignUp text-center h-full flex flex-col items-center justify-center align-middle">
      <>
        <motion.div
          className="flex justify-center"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
        >
          <div className="flex flex-col items-center">
            <span className="sr-only">Create an account</span>
            <h1 className="text-gold-700 text-2xl font-bold tracking-tight sm:text-4xl mb-12">
              Signup
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
          <SignupForm />
        </motion.div>
      </>
    </div>
  );
}

export default Signup;
