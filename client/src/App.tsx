import { Routes, Route } from "react-router-dom";
import Layout from "@/layout/Layout";
import AuthLayout from "@/layout/AuthLayout";
import AdminLayout from "@/layout/AdminLayout";
import Home from "@/pages/home/Home";
import Demo from "@/pages/demo/Demo";
import Login from "@/pages/login/Login";
import Signup from "@/pages/signup/Signup";
import Test from "@/pages/test/Test";
import Chat from "@/pages/chat/Chat";
import { useAuth } from "@/hooks/use-auth";
import LoadingAnimation from "@/components/LoadingAnimation";

/**
 * Main App component
 * Defines the routing structure for the entire application
 * Each route is associated with a specific tool or feature
 */
const App = () => {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return <LoadingAnimation />;
  }
  return (
    <Routes>
      <Route element={user ? <AuthLayout /> : <Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/demo" element={<Demo />} />
      </Route>
      <Route element={<AuthLayout />}>
        <Route path="/chat" element={<Chat />} />
      </Route>
      <Route element={<AdminLayout />}>
        <Route path="/test" element={<Test />} />
        <Route path="/demo" element={<Demo />} />
      </Route>
    </Routes>
  );
};

export default App;
