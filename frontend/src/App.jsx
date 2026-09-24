import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import AIAssistant from "./pages/AIAssistant";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ai-assistant" element={<AIAssistant />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;