import { motion } from "framer-motion";

function Prompts() {
  return (
    <motion.div
      className="_Prompts text-center mb-12"
      key="prompts"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="text-gold-700 text-2xl font-bold sm:text-4xl">
        Prompts Page
      </h1>
    </motion.div>
  );
}

export default Prompts;
