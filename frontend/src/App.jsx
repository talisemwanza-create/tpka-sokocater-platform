
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";

import Home from "./pages/customer/Home";
import CatererListing from "./pages/customer/CatererListing";
import CatererDetail from "./pages/customer/CatererDetail";
import BookingForm from "./pages/customer/BookingForm";

import Dashboard from "./pages/caterer/Dashboard";
import CatererForm from "./pages/caterer/CatererForm";

import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        {/* Customer pages */}
        <Route path="/" element={<Home />} />
        <Route path="/caterers" element={<CatererListing />} />
        <Route path="/caterer/:id" element={<CatererDetail />} />
        <Route path="/booking" element={<BookingForm />} />

        {/* Authentication pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Caterer pages */}
        <Route path="/caterer/dashboard" element={<Dashboard />} />
        <Route path="/caterer/profile" element={<CatererForm />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
