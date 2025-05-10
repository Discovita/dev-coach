import { ChatInterface } from "@/pages/chat/components/ChatInterface";
import { motion } from "framer-motion";

const Chat = () => {
  return (
    <motion.div className="_Chat relative z-10 flex flex-col h-full">
      <div className="flex flex-col xl:flex-row items-start flex-1 min-h-0">
        <div className="flex flex-col w-full xl:flex-1 min-w-0 overflow-hidden h-full min-h-0 xl:mr-4">
          <ChatInterface />
        </div>
      </div>
    </motion.div>
  );
};

export default Chat;
