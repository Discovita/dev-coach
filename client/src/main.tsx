import { StrictMode, lazy, Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import * as TanStackQueryProvider from './integrations/tanstack-query/root-provider.tsx'
import App from './App.tsx'
import './styles.css'
import reportWebVitals from './reportWebVitals.ts'
import { Toaster } from "@/components/ui/sonner";

const ReactQueryDevtools = import.meta.env.DEV
  ? lazy(() =>
      import("@tanstack/react-query-devtools").then((mod) => ({
        default: mod.ReactQueryDevtools,
      }))
    )
  : () => null;

const TanStackQueryProviderContext = TanStackQueryProvider.getContext()

const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <TanStackQueryProvider.Provider {...TanStackQueryProviderContext}>
        <App />
        <Suspense>
          <ReactQueryDevtools />
        </Suspense>
        <Toaster closeButton position="bottom-right" />
      </TanStackQueryProvider.Provider>
    </StrictMode>,
  )
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
