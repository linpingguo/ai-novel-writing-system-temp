import { BrowserRouter, Routes, Route } from 'react-router-dom'
import router from './router'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {router.map((route, index) => (
          <Route
            key={index}
            path={route.path}
            element={<route.element />}
          />
        ))}
      </Routes>
    </BrowserRouter>
  )
}

export default App
