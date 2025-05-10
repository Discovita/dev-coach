import { motion } from "framer-motion";

function Home() {
  return (
    <motion.div
      className="_Home text-center h-full w-full flex items-center justify-center align-middle flex-col gap-4"
      key="home"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="text-gold-700 text-2xl font-bold sm:text-4xl">
        Welcome to the Coach
      </h1>
    </motion.div>
  );
}

export default Home;
