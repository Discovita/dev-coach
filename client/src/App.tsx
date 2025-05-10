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
import Prompts from "@/pages/prompts/Prompts";
import { User } from "@/types/user";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { SessionRestorer } from "@/components/SessionRestorer";

/**
 * Main App component
 * Defines the routing structure for the entire application
 * Each route is associated with a specific tool or feature
 */
const App = () => {
  // Get user profile and isAdmin flag from TanStack Query cache (populated after login/register)
  const profile = useReactiveQueryData<User>(["user", "profile"]);
  const isAdmin = useReactiveQueryData<boolean>(["user", "isAdmin"]);

  if (profile && isAdmin) {
    // User is admin
    return (
      <>
        <SessionRestorer />
        <Routes>
          <Route element={<AdminLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/test" element={<Test />} />
            <Route path="/prompts" element={<Prompts />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>
        </Routes>
      </>
    );
  }
  if (profile) {
    // User is authenticated but not admin
    return (
      <>
        <SessionRestorer />
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>
        </Routes>
      </>
    );
  }
  // User is not logged in
  return (
    <>
      <SessionRestorer />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/demo" element={<Demo />} />
        </Route>
      </Routes>
    </>
  );
};

export default App;
