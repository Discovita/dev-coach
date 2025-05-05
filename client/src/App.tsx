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
import { useAuth } from "@/hooks/use-auth";
import LoadingAnimation from "@/components/LoadingAnimation";

/**
 * Main App component
 * Defines the routing structure for the entire application
 * Each route is associated with a specific tool or feature
 */
const App = () => {
  const { user, isLoading, isAdmin } = useAuth();
  console.log("App component - user:", user);
  if (isLoading) {
    return <LoadingAnimation />;
  }
  if (user && isAdmin) {
    console.log("User is admin");
    return (
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
    );
  }
  if (user) {
    console.log("User is not admin");
    return (
      <Routes>
        <Route element={<AuthLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Route>
      </Routes>
    );
  }
  return (
    console.log("User is not logged in"),
    (
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/demo" element={<Demo />} />
        </Route>
      </Routes>
    )
  );
};

export default App;
