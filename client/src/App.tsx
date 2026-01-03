import { Routes, Route } from "react-router-dom";
import PublicLayout from "@/layout/PublicLayout";
import AuthLayout from "@/layout/AuthLayout";
import AdminLayout from "@/layout/AdminLayout";
import Home from "@/pages/home/Home";
import Demo from "@/pages/demo/Demo";
import Login from "@/pages/login/Login";
import Signup from "@/pages/signup/Signup";
import Test from "@/pages/test/Test";
import Chat from "@/pages/chat/Chat";
import Prompts from "@/pages/prompts/Prompts";
import Images from "@/pages/images/Images";
import { useProfile } from "@/hooks/use-profile";
import { useIsAdmin } from "@/hooks/use-is-admin";
import { SessionRestorer } from "@/components/SessionRestorer";

/**
 * Main App component
 * Defines the routing structure for the entire application
 * Each route is associated with a specific tool or feature
 */
const App = () => {
  // Get user profile and isAdmin flag using hooks (profile is populated after login/register or by SessionRestorer)
  const { profile } = useProfile();
  const isAdmin = useIsAdmin();

  if (profile && isAdmin) {
    console.log("Showing admin routes", profile, isAdmin);
    return (
      <>
        <SessionRestorer />
        <Routes>
          <Route element={<AdminLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/test" element={<Test />} />
            <Route path="/prompts" element={<Prompts />} />
            <Route path="/images" element={<Images />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>
        </Routes>
      </>
    );
  }
  if (profile) {
    console.log("Showing auth routes", profile, isAdmin);
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
  console.log("Showing public routes", profile, isAdmin);
  return (
    <>
      <SessionRestorer />
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Route>
      </Routes>
    </>
  );
};

export default App;
